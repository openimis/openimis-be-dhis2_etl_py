from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Callable, Union


@dataclass
class DHISCode:
    code: str


@dataclass
class Period:
    from_date: datetime
    period_type: str
    representation: str
    to_date: datetime = None


@dataclass
class ADXDataValueAggregation:
    label_name: str
    label_value: str


@dataclass
class ADXDataValue:
    data_element: str
    value: str
    aggregations: List[ADXDataValueAggregation]


@dataclass
class ADXMappingGroup:
    org_unit: str
    period: str
    data_set: str
    comment: str
    data_values: List[ADXDataValue]  # TODO: Defined automatically based on queryset of ADX Mapping and categories


@dataclass
class ADXMapping:
    name: str
    groups: List[ADXMappingGroup]
