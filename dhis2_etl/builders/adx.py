import itertools
import logging
from typing import Collection, List, Type
from datetime import datetime
from dhis2_etl.models.adx.data import (ADXDataValue, ADXDataValueAggregation,
                                       ADXMapping, ADXMappingGroup, Period)
from dhis2_etl.models.adx.definition import (ADXMappingCubeDefinition,
                                             ADXMappingDataValueDefinition,
                                             ADXMappingGroupDefinition)
from django.db.models import F, Model, Q , When, Case, Value, Subquery,QuerySet,Window

from numpy import unique
from dhis2_etl.utils import  clean_code

logger = logging.getLogger('openIMIS')

from datetime import date
from dhis2_etl.utils import toDateStr
def get_annotation_case(key, category_options):
    #whens = [When(co.filter, then=Value(f"{co.code}")) for co in valid_options]
    return {
        key:   get_case(category_options)
    }
    
def get_case(category_options):
    whens = [When(co.filter, then=Value(f"{co.code}")) for co in category_options if co.filter]
    return Case(
                *whens
           )
    
def get_annotation_window(key, categories, agg_fct):
    return {
        key:  Window(
            expression= agg_fct,
            partition_by = [get_case(c.category_options) if c.path is None else c.path for c in categories]
           )
    }
    
def get_annotation_aggregate(key, fct):
    return {
        key:  fct
    }
    
def get_sql_name(name):
    return f"cat_{name}"

def revert_sql_name(sql_name):
    return sql_name[4:]


DJANGO_LOOP_UP = [
   'contains',
   'icontains',
   'date',
   'day',
   'endswith',
   'iendswith',
   'exact',
   'iexact',
   'in',
   'isnull',
   'gt',
   'gte',
   'hour',
   'lt',
   'lte',
   'minute',
   'month',
   'quarter',
   'range',
   'regex',
   'iregex',
   'second',
   'startswith',
   'istartswith',
   'time',
   'week',
   'week_day',
   'iso_week_day',
   'year',
   'iso_year',

]

def get_field_from_Q(filter):
    fields = []
    for c in filter.children:
        if isinstance(c,Q):
            sub =  get_field_from_Q(c)
            if len(sub)>0:
                fields+=sub
        elif isinstance(c,tuple) and isinstance(c[0], str):
                k_arr = c[0].split('__')
                fields.append('__'.join(k_arr[:-1]) if k_arr[-1] in DJANGO_LOOP_UP else c[0])
                
        else:
            logger.warning('not suported %s', c.__class__)
        
            
    return fields
         

class ADXDataValueBuilder:
    def __init__(self, adx_mapping_definition: ADXMappingDataValueDefinition):
        self.categories = adx_mapping_definition.categories
        self.aggregation_func = adx_mapping_definition.aggregation_func
        self.period_filter_func = adx_mapping_definition.period_filter_func
        self.data_element = adx_mapping_definition.data_element
        self.dataset_from_orgunit_func = adx_mapping_definition.dataset_from_orgunit_func

    def get_defaut_cat_options(self, cat_name):
         for c in self.categories:
            if cat_name == c.category_name:
                for o in c.category_options:
                    if o.is_default:
                        return o.code 
    def create_adx_data_value(self, organization_unit: Model, period: Period) -> List[ADXDataValue]:
        data_values = []
        fields_impacted = []
        annotation = []
        queryset = self._get_filtered_queryset(organization_unit, period)
        if len(self.categories)>0:
            # get list of fields in the cat 
            
            
            for c in self.categories:
                for o in c.category_options:
                    if o.filter:
                        sub = get_field_from_Q(o.filter)
                        if len(sub)>0:
                            fields_impacted+=sub
                if c.path is None:
                    annotation.append(get_annotation_case( get_sql_name(c.category_name) ,c.category_options))
                else:
                    annotation.append({get_sql_name(c.category_name): F(c.path)})
                    fields_impacted+=[c.path]

                # annotate with a case
            #queryset = queryset.annotate(**get_annotation_aggregate('adx_value' ,self.aggregation_func)).values('adx_value',*[get_sql_name(c.category_name) for c in self.categories])
            queryset = queryset.values('id',*unique(fields_impacted))
            for a in annotation:
                queryset = queryset.annotate(**a)
            queryset = queryset.annotate(**get_annotation_window('adx_value' ,self.categories,self.aggregation_func)).values('adx_value',*[get_sql_name(c.category_name) for c in self.categories]).distinct() # *[get_sql_name(c.category_name) for c in self.categories]

            for item in queryset:
                aggregations = []
                out_of_cat = False
                for k,v in item.items():
                    if v is None:
                        cat_name = revert_sql_name(k)
                        v = self.get_defaut_cat_options(cat_name)
                        if v is None:
                            out_of_cat = True
                        aggregations.append(ADXDataValueAggregation(clean_code(cat_name), v))
                    elif k == '':
                        logger.warning('cannot parse desagregation')
                    elif k != 'adx_value':
                        aggregations.append(ADXDataValueAggregation(clean_code(revert_sql_name(k)), v))
                if not out_of_cat:
                    data_values.append(ADXDataValue(
                        data_element=self.data_element,
                        value=str(item['adx_value']),
                        aggregations=aggregations
                    ))
                else:
                    logger.debug('value %s is out of category definition %s', str(item['adx_value']), " ".join([f"{a.label_name}: {a.label_value}"  for a in aggregations]) )
 
            #data_values.append(self._create_data_value_for_group_filtering(qs, group_definition))
        else:
            # Create single combined view if no categories available
            data_values.append(ADXDataValue(
                        data_element=self.data_element,
                        value=str(queryset.aggregate(value=self.aggregation_func)['value']),
                        aggregations=[]))
        return data_values

    def _filter_queryset_by_category(self, queryset, group_filtering):
        for q_filter in group_filtering:
            queryset = queryset.filter(q_filter)
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
        qs = self.dataset_from_orgunit_func(organization_unit)
        if self.period_filter_func is not None:
            qs = self.period_filter_func(qs, period)
        # this does not make sens for ADX as the sum could be across all data
        #else:
        #    qs = _filter_period(qs, period)
        return qs


def _filter_period(qs, period):
    return qs.filter(validity_from__gte=period.from_date, validity_from__lte=period.to_date) \
        .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))


class ADXGroupBuilder:
    def __init__(self, 
                 adx_mapping_definition: ADXMappingGroupDefinition,
                 data_value_mapper: Type[ADXDataValueBuilder] = ADXDataValueBuilder):
        self.adx_mapping_definition = adx_mapping_definition
        self.data_value_mapper = data_value_mapper

    def create_adx_group(self,  period: Period, org_unit_obj: Model, org_unit: str):
        return ADXMappingGroup(
            complete_date = toDateStr(date.today()),
            org_unit=org_unit,
            period=period.representation,
            data_set=self.adx_mapping_definition.data_set,
            data_values=self._build_group_data_values(period, org_unit_obj),
            comment=self.adx_mapping_definition.comment
        )
        
    def create_adx_groups(self,  period: Period, org_unit_obj: Model, org_unit: str):
        if self.adx_mapping_definition.aggregations is None or len(self.adx_mapping_definition.aggregations)==0:
            return [self.create_adx_group( period, org_unit_obj, org_unit)]
        else:
            groups = []
            groups_aggregations_combo = {}
            groups_aggregations_combo_datavalue = {}
            dv = self._build_group_data_values(period, org_unit_obj)
            group_aggregations_names = [c.category_name.upper() for c in self.adx_mapping_definition.aggregations]
            for d in dv:
                # define the dv combo managed on group level 
                group_combo = [ aggr for aggr in d.aggregations if aggr.label_name in group_aggregations_names ]
                if len(group_combo) != len(group_aggregations_names):
                    logger.error(f'mismatch, dataset {self.adx_mapping_definition.data_set} aggregation not found on  dataElement {d.data_element} aggregation')
                group_combo_key = "_".join([aggr.label_value for aggr in group_combo])
                # Save the actual combo
                if group_combo_key not in groups_aggregations_combo:
                    groups_aggregations_combo_datavalue[group_combo_key] = []
                    groups_aggregations_combo[group_combo_key] = group_combo
                # aggregation on group level, should be remove from dv
                for aggr in group_combo:
                    if aggr not in d.aggregations:
                        logger.error(f'{aggr.label_name} not in the datavalue definition')
                    d.aggregations.remove(aggr)
                groups_aggregations_combo_datavalue[group_combo_key].append(d)
            #get the possible or actual groups
            for group_combo_key in groups_aggregations_combo:
                groups.append( ADXMappingGroup(
                    complete_date = toDateStr(date.today()),
                    org_unit=org_unit,
                    period=period.representation,
                    data_set=self.adx_mapping_definition.data_set,
                    data_values=groups_aggregations_combo_datavalue[group_combo_key],
                    aggregations=groups_aggregations_combo[group_combo_key],
                    comment=self.adx_mapping_definition.comment
                ))
            return groups

    def _build_group_data_values(self, period: Period, org_unit_obj: object):
        data_values = []
        for data_value in self.adx_mapping_definition.data_values:
            values = self.data_value_mapper(data_value).create_adx_data_value(org_unit_obj, period)
            data_values.extend(values)
        return data_values


class ADXBuilder:
    def __init__(self, adx_mapping_definition: ADXMappingCubeDefinition,
                 group_mapper: Type[ADXGroupBuilder] = ADXGroupBuilder):
        self.adx_mapping_definition = adx_mapping_definition
        self.group_mapper = group_mapper

    def create_adx_cube(self, period: str, org_units: Collection[Model]) -> ADXMapping:
        period = self._period_str_to_obj(period)
        return ADXMapping(
            groups=self._build_adx_groups(period, org_units)
        )

    def _build_adx_groups(self, period: Period, org_units: Collection[Model]):
        groups = []
        for group_definition in self.adx_mapping_definition.groups:
            group_mapper = self.group_mapper(group_definition)
            for org_unit_obj in org_units:
                org_unit = group_definition.to_org_unit_code_func(org_unit_obj)
                groups+=group_mapper.create_adx_groups(period, org_unit_obj, org_unit)
        return groups

    def _period_str_to_obj(self, period: str):
        return self.adx_mapping_definition.period_type.build_period(period)



        

