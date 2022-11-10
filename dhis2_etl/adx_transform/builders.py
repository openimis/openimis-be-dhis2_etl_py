import itertools

from django.db.models import Q, Model, F
from typing import Collection, List, Type
from uuid import UUID

from dhis2_etl.adx_transform.adx_models.adx_data import Period, ADXDataValue, ADXDataValueAggregation, ADXMappingGroup, \
    ADXMapping
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingDataValueDefinition, ADXMappingGroupDefinition, \
    ADXMappingCubeDefinition
from dhis2_etl.utils import build_dhis2_id


class ADXDataValueBuilder:
    def __init__(self, adx_mapping_definition: ADXMappingDataValueDefinition):
        self.categories = adx_mapping_definition.categories
        self.aggregation_func = adx_mapping_definition.aggregation_function
        self.data_element = adx_mapping_definition.data_element
        self.related_from_dataset_func = adx_mapping_definition.related_from_dataset_func

    def create_adx_data_value(self, organization_unit: Model, period: Period) -> List[ADXDataValue]:
        data_values = []
        queryset = self._get_filtered_queryset(organization_unit, period)
        if category_groups := self.__category_groups:
            for group_definition, group_filtering in category_groups:
                qs = self._filter_queryset_by_category(queryset.all(), group_filtering)
                data_values.append(self._create_data_value_for_group_filtering(qs, group_definition))
        else:
            # Create single combined view if no categories available
            data_values.append(self._create_data_value_for_group_filtering(queryset.all(), []))
        return data_values

    def _filter_queryset_by_category(self, queryset, group_filtering):
        for filter_func in group_filtering:
            queryset = filter_func(queryset)
        return queryset

    def _create_data_value_for_group_filtering(self, queryset, group_definition):
        return ADXDataValue(
            data_element=self.data_element,
            value=self.aggregation_func(queryset),
            aggregations=self.__create_aggregations(group_definition)
        )

    def __create_aggregations(self, group_definition):
        return [ADXDataValueAggregation(label, value) for label, value in group_definition]

    @property
    def __category_groups(self):
        """
        Combine all filter variances.
        :return: list of two element tuples where first element is category group information
        and key is function filtering queryset
        """
        filters = []
        options = [g.category_options for g in self.categories]
        category_names = [o.category_name for o in self.categories]
        for combined_option in itertools.product(*options):
            labels = [o.code for o in combined_option]
            group_label = zip(category_names, labels)
            filters.append((group_label, [o.filter for o in combined_option]))
        return filters

    def _get_filtered_queryset(self, organization_unit, period):
        qs = self.related_from_dataset_func(organization_unit)
        qs = self._filter_period(qs, period)
        return qs

    def _filter_period(self, qs, period):
        return qs.filter(validity_from__gte=period.from_date, validity_from__lte=period.to_date)\
            .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))


class ADXGroupBuilder:
    def __init__(self, adx_mapping_definition: ADXMappingGroupDefinition,
                 data_value_mapper: Type[ADXDataValueBuilder] = ADXDataValueBuilder):
        self.adx_mapping_definition = adx_mapping_definition
        self.data_value_mapper = data_value_mapper

    def create_adx_group(self, period: Period, org_unit: UUID):
        return ADXMappingGroup(
            org_unit=build_dhis2_id(org_unit),
            period=period.representation,
            data_set=self.adx_mapping_definition.dataset_repr,
            data_values=self._build_group_data_values(period, org_unit),
            comment=self.adx_mapping_definition.comment
        )

    def _build_group_data_values(self, period: Period, org_unit: UUID):
        data_values = []
        for data_value in self.adx_mapping_definition.data_values:
            org_unit_obj = self.adx_mapping_definition.dataset.objects.get(uuid=org_unit)
            values = self.data_value_mapper(data_value).create_adx_data_value(org_unit_obj, period)
            data_values.extend(values)
        return data_values


class ADXBuilder:
    def __init__(self, adx_mapping_definition: ADXMappingCubeDefinition,
                 group_mapper: Type[ADXGroupBuilder] = ADXGroupBuilder):
        self.adx_mapping_definition = adx_mapping_definition
        self.group_mapper = group_mapper

    def create_adx_cube(self, period: str, org_units: Collection[UUID]) -> ADXMapping:
        period = self._period_str_to_obj(period)
        return ADXMapping(
            name=self.adx_mapping_definition.name,
            groups=self._build_adx_groups(period, org_units)
        )

    def _build_adx_groups(self, period: Period, org_units: Collection[UUID]):
        groups = []
        for group_definition in self.adx_mapping_definition.groups:
            group_mapper = self.group_mapper(group_definition)
            for org_unit in org_units:
                groups.append(group_mapper.create_adx_group(period, org_unit))
        return groups

    def _period_str_to_obj(self, period: str):
        return self.adx_mapping_definition.period_type.build_period(period)
