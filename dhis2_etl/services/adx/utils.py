from datetime import datetime, timedelta
from typing import Any

from django.db.models import QuerySet, Sum, Model, Q, Value, F

from dhis2_etl.adx_transform.adx_models.adx_data import Period
from dhis2_etl.utils import build_dhis2_id


def get_qs_count(qs: QuerySet) -> str:
    return str(qs.count())


def get_qs_sum(qs: QuerySet, field: str) -> str:
    return str(qs.aggregate(Sum(field))[f'{field}__sum'] or 0)


def get_location_filter(location: Model, fk: str = 'location') -> dict[str, Model]:
    return {
        f'{fk}': location,
        f'{fk}__parent': location,
        f'{fk}__parent__parent': location,
        f'{fk}__parent__parent__parent': location,
    }


def get_last_day_of_last_month(any_day: datetime) -> datetime:
    return any_day - timedelta(days=any_day.day)


def filter_with_prefix(qs: QuerySet, key: str, value: Any, prefix: str = '') -> QuerySet:
    return qs.filter(**{f'{prefix}{key}': value})


def filter_period(qs: QuerySet, period: Period) -> QuerySet:
    return qs.filter(validity_from__gte=period.from_date, validity_from__lte=period.to_date) \
        .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))


def get_org_unit_code(model: Model) -> str:
    return build_dhis2_id(model.uuid)
