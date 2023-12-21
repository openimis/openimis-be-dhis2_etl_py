from datetime import datetime, timedelta
from typing import Any, Dict

from django.db.models import QuerySet, Sum, Model, Q, F, Exists, OuterRef,Value
from django.db.models.functions import  Coalesce
from core import filter_validity
from contribution.models import Premium
from dhis2_etl.models.adx.data import Period
from dhis2_etl.utils import build_dhis2_id


def get_qs_count(qs: QuerySet) -> str:
    return str(qs.count())


def get_qs_sum(qs: QuerySet, field: str) -> str:
    return str(qs.aggregate(Sum(field))[f'{field}__sum'] or 0)


def get_location_filter(location: Model, fk: str = 'location') -> Dict[str, Model]:
    return {
        f'{fk}': location,
        f'{fk}__parent': location,
        f'{fk}__parent__parent': location,
        f'{fk}__parent__parent__parent': location,
    }




def get_first_day_of_last_month(date = None) -> datetime:
    if date is None: 
        date = datetime.now()
    elif isinstance(date,str):
        date = datetime.strptime(date, '%Y-%m-%d')
    if isinstance(date,datetime):
        return (date - timedelta(days=date.day)).replace(day=1)

def filter_with_prefix(qs: QuerySet, key: str, value: Any, prefix: str = '') -> QuerySet:
    return qs.filter(**{f'{prefix}{key}': value})


def q_with_prefix(key: str, value: Any, prefix: str = '') -> Q:
    return Q(**{f'{prefix}{key}': value})

def filter_period(qs: QuerySet, period: Period) -> QuerySet:
    return qs.filter(validity_from__gte=period.from_date, validity_from__lte=period.to_date) \
        .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))


def get_contribution_period_filter(qs, p):
    return qs.filter(pay_date__gte=p.from_date,pay_date__lt = p.to_date)


def get_claim_period_filter(qs, period, prefix=''):
    return qs.annotate(ref_date=Coalesce(f'{prefix}date_to',f'{prefix}date_from'))\
            .filter(ref_date__gte = period.from_date)\
            .filter(ref_date__lt = period.to_date)\
            .filter(*filter_validity())


def get_claim_details_period_filter(qs, period):
    return get_claim_period_filter(qs, period, prefix='claim__')


def get_org_unit_code(model: Model) -> str:
    return build_dhis2_id(model.uuid)


def get_fully_paid():
    return Q(policy_value_sum__lte=Sum('family__policies__premiums__amount'))


def get_partially_paid():
    return Q(policy_value_sum__gt=Sum('family__policies__premiums__amount'))


def not_paid():
    return Q(family__policies__premiums__amount__isnull=True)


def valid_policy(period):
    return (Q(family__policies__effective_date__lte=period.to_date)
            & Q(family__policies__expiry_date__lt=period.to_date)) \
        & Q(family__policies__validity_to__isnull=True)
