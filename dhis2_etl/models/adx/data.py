from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable, List, Union
from dhis2_etl.models.dhis2.type import dateStr

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
    complete_date: dateStr
    org_unit: str
    period: str
    data_set: str
    comment: str
    data_values: List[ADXDataValue]  # TODO: Defined automatically based on queryset of ADX Mapping and categories
    aggregations: List[ADXDataValueAggregation] = None



@dataclass
class ADXMapping:
    groups: List[ADXMappingGroup]
    exported: datetime
    
    def __init__(self,groups: List[ADXMappingGroup] ):
        self.groups = groups
        self.exported = datetime.now() 
