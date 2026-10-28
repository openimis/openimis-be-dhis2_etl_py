from datetime import datetime, timedelta
from typing import Any, Dict

from django.db.models import (
    QuerySet,
    Sum,
    Model,
    Q,
    F,
    Exists,
    OuterRef,
    Value,
    Case,
    When,
    CharField,
)
from django.db.models.functions import Coalesce
from claim.models import Claim
from insuree.models import InsureePolicy
from policy.models import Policy
from django_adx.models.adx.data import Period
from dhis2_etl.utils import build_dhis2_id


def get_qs_count(qs: QuerySet) -> str:
    return str(qs.count())


def get_qs_sum(qs: QuerySet, field: str) -> str:
    return str(qs.aggregate(Sum(field))[f"{field}__sum"] or 0)


def get_location_filter(location: Model, fk: str = "location") -> Dict[str, Model]:
    return {
        f"{fk}": location,
        f"{fk}__parent": location,
        f"{fk}__parent__parent": location,
        f"{fk}__parent__parent__parent": location,
    }


def get_first_day_of_last_month(date=None) -> datetime:
    if date is None:
        date = datetime.now()
    elif isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")
    if isinstance(date, datetime):
        return (date - timedelta(days=date.day)).replace(day=1)


def filter_with_prefix(
    qs: QuerySet, key: str, value: Any, prefix: str = ""
) -> QuerySet:
    return qs.filter(**{f"{prefix}{key}": value})


def q_with_prefix(key: str, value: Any, prefix: str = "") -> Q:
    return Q(**{f"{prefix}{key}": value})


def get_period_last_day(period: Period) -> datetime:
    # period.to_date is exclusive: first day of the next period
    return period.to_date - timedelta(days=1)


def filter_period(qs: QuerySet, period: Period) -> QuerySet:
    return qs.filter(
        validity_from__gte=period.from_date, validity_from__lt=period.to_date
    ).filter(
        Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F("id"))
    )


def get_contribution_period_filter(qs, p):
    return qs.filter(pay_date__gte=p.from_date, pay_date__lt=p.to_date)


def get_claim_period_filter(qs, period, prefix=""):
    return (
        qs.annotate(ref_date=Coalesce(f"{prefix}date_to", f"{prefix}date_from"))
        .filter(ref_date__gte=period.from_date)
        .filter(ref_date__lt=period.to_date)
        .filter(*Claim.filter_validity())
    )


def get_claim_details_period_filter(qs, period):
    return get_claim_period_filter(qs, period, prefix="claim__")


def get_org_unit_code(model: Model) -> str:
    return build_dhis2_id(model.uuid)


def get_fully_paid():
    return Q(policy_value_sum__lte=Sum("family__policies__premiums__amount"))


def get_partially_paid():
    return Q(policy_value_sum__gt=Sum("family__policies__premiums__amount"))


def not_paid():
    return Q(family__policies__premiums__amount__isnull=True)


def valid_policy(period):
    # policy covering at least one day between the first and last day of the period
    return (
        Q(family__policies__start_date__lte=get_period_last_day(period))
        & Q(family__policies__expiry_date__gte=period.from_date)
    ) & Q(family__policies__validity_to__isnull=True)


def get_policy_status_annotation(period, insuree_level=False):
    # Status of the most relevant policy for the period, ranked
    # ACTIVE > SUSPENDED > IDLE > READY > EXPIRED, NO_POLICY otherwise.
    # Policy.status is the current status only: a policy now EXPIRED that
    # covered the period was active during it, so it is reported as ACTIVE.
    # Computed with subqueries so rows are not multiplied by the policy join.
    # Insuree level relies on the individual coverage dates of InsureePolicy.
    last_day = get_period_last_day(period)
    if insuree_level:
        # historical insuree rows point to the current one through legacy_id
        policies = InsureePolicy.objects.filter(
            insuree_id=Coalesce(OuterRef("legacy_id"), OuterRef("pk")),
            validity_to__isnull=True,
            start_date__lte=last_day,
        )
        status = "policy__status"
        coverage = Q(effective_date__lte=last_day, expiry_date__gte=period.from_date)
    else:
        policies = Policy.objects.filter(
            family=OuterRef("family_id"),
            validity_to__isnull=True,
            start_date__lte=last_day,
        )
        status = "status"
        coverage = Q(expiry_date__gte=period.from_date)
    return Case(
        When(
            Exists(
                policies.filter(
                    coverage,
                    **{
                        f"{status}__in": [
                            Policy.STATUS_ACTIVE,
                            Policy.STATUS_EXPIRED,
                        ]
                    },
                )
            ),
            then=Value("ACTIVE"),
        ),
        When(
            Exists(policies.filter(**{status: Policy.STATUS_SUSPENDED})),
            then=Value("SUSPENDED"),
        ),
        When(
            Exists(policies.filter(**{status: Policy.STATUS_IDLE})),
            then=Value("IDLE"),
        ),
        When(
            Exists(policies.filter(**{status: Policy.STATUS_READY})),
            then=Value("READY"),
        ),
        When(Exists(policies), then=Value("EXPIRED")),
        default=Value("NO_POLICY"),
        output_field=CharField(),
    )
