from dataclasses import dataclass
from typing import Callable, Collection, List, Type, Optional
from uuid import UUID

from dhis2_etl.models.adx.data import Period
from dhis2_etl.models.adx.time_period import PeriodType
from django.db.models import Model, QuerySet, Q
from pydantic import  BaseModel

@dataclass
class ADXCategoryOptionDefinition:
    code: str
    name: str
    filter: Q = None  # Filtering function takes queryset instance as argument and returns another queryset
    is_default: bool = False


@dataclass
class ADXMappingCategoryDefinition:
    category_name: str
    category_options: List[ADXCategoryOptionDefinition]
    path: Optional[str] = None
    group_attribute: bool = False



@dataclass
class ADXMappingDataValueDefinition:
    data_element: str
    aggregation_func: Callable[[QuerySet], str]
    dataset_from_orgunit_func: Callable
    period_filter_func: Callable[[QuerySet, Period], QuerySet]
    categories: List[ADXMappingCategoryDefinition]



@dataclass
class ADXMappingGroupDefinition:
    comment: str
    data_set: str
    org_unit_type: Type[Model]  # HF Etc.
    data_values: List[ADXMappingDataValueDefinition]
    to_org_unit_code_func: Callable[[Model], str]
    aggregations : List[ADXMappingCategoryDefinition] = None

    @property
    def dataset_repr(self) -> str:
        return str(self.data_set.__name__).upper()


@dataclass
class ADXMappingCubeDefinition:
    period_type: PeriodType  # Currently handled in ISO Format
    groups: List[ADXMappingGroupDefinition]
    org_units: Collection[UUID] = None  # UUIDs of objects stored in Model, can be queryset result or list
