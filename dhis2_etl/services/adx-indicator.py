import datetime
from dateutil.relativedelta import relativedelta
from dhis2 import api

from django.db.models import Q, Sum,OuterRef, Exists
from dataclasses import asdict
from typing import List
from xml.etree import ElementTree

from django.test import TestCase
from location.models import HealthFacility, Location
from payment.models import Premium
from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.adx_transform.builders import ADXBuilder
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingDataValueDefinition, \
    ADXMappingCategoryDefinition, ADXCategoryOptionDefinition, ADXMappingCubeDefinition, ADXMappingGroupDefinition
from dhis2_etl.utils import build_dhis2_id
from insuree.models import Insuree
from insuree.models import Gender
from dhis2_etl.adx_transform.adx_models.adx_time_period import ISOFormatPeriodType, PeriodParsingException

from ..models.dhis2Enum import ImportStrategy, MergeMode

def get_age_range_dict(min, max, step, refDate):
    slices = []
    for i in range(min,max,step):
        upper = i+step
        #born before 
        end_date =  refDate-relativedelta(years=i)
        start_date =  datetime.datetime.now() -relativedelta(years=upper)+datetime.timedelta(days=1)
        slices.append(ADXCategoryOptionDefinition(
            code=str(i)+"-"+str(upper-1),
            filter=lambda insuree_qs: insuree_qs.filter(dob__range=(start_date, end_date))))
        
def get_age_categories(min, max, step, refDate):

     return ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=[
            get_age_range_dict(min, max, step, refDate)
        ]
    )

SEX_CATEGORY_DEFINITION = ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", filter=lambda insuree_qs: insuree_qs.filter(gender__code='M')),
            ADXCategoryOptionDefinition(
                code="F", filter=lambda insuree_qs: insuree_qs.filter(gender__code='F'))
        ]
    )
def get_valid_policy_filter(refDate):
    return (Q(family__policies__effective_date__lte=refDate)\
            & Q(family__policies__expiry_date__lt=refDate))\
            & Q(family__policies__validity_to__isnull=True)
def get_fully_payed():
    return Q(family__policies__value__lte = Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')).aggregate(sum=Sum('amount'))['sum'])
def get_partialy_payed():
    return Q(family__policies__value__gt = Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')).aggregate(sum=Sum('amount'))['sum'])
def not_payed():
    return Exists(Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')))
    

# Fully payed, partially payed, not payed, not covered
def get_payment_status_categories(refDate):
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(refDate) & get_fully_payed())),
            ADXCategoryOptionDefinition(
                code="partialy-payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(refDate) & get_partialy_payed())),
            ADXCategoryOptionDefinition(
                code="not-payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(refDate) & not_payed())),
            ADXCategoryOptionDefinition(
                code="not-covered", filter=lambda insuree_qs: insuree_qs.filter(~get_valid_policy_filter(refDate)))
        ]
    )

def get_insuree_registration_cube(refDate):
    return ADXMappingCubeDefinition(
        name='Insuree per location, sex and age group',
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                dataset=Location,
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        related_from_dataset_func=lambda l: l.insuree_set.filter(validity_to__isnull=True),
                        aggregation_function=lambda insuress_qs: str(insuress_qs.count()),
                        categories=[get_age_categories(0, 120, 10, refDate), SEX_CATEGORY_DEFINITION]
                    )
                ]
            )
        ]
    )


def get_number_of_family_cube(refDate):
    return ADXMappingCubeDefinition(
        name='number of family size per location',
        period_type=ISOFormatPeriodType(),
        groups=[
            ADXMappingGroupDefinition(
                comment="Test Comment",
                dataset=HealthFacility,
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="FAMILY_SIZE",
                        related_from_dataset_func=lambda l: l.insuree_set.filter(head=True).filter(validity_to__isnull=True),
                        aggregation_function=lambda family_qs: str(family_qs.count()),
                        categories=[get_age_categories(0, 120, 10, refDate), SEX_CATEGORY_DEFINITION,get_payment_status_categories(refDate)]
                    )
                ]
            )
        ]
    )

def last_day_of_last_month(any_day):
    return any_day - datetime.timedelta(days=any_day.day)

#Nombre d’adhérents par district, par municipalité, par sexe, par âge 
def post_insuree_adx(refDate, period):
    org_units =  list(Location.all().filter(validity_to__isnull = True).filter(type = 'V').values_list('uuid', flat=True))
    builder = ADXBuilder(get_insuree_registration_cube(refDate))
    insuree_data =  builder.create_adx_cube(period, org_units)
    return api.post(
            'dataValueSets',
            xml=insuree_data,
            params={'mergeMode': MergeMode.merge})

#Taille moyenne des familles adhérentes par district, par municipalité -> send nb family
def post_family_size_adx(refDate, period):
    org_units =  list(Location.all().filter(validity_to__isnull = True).filter(type = 'V').values_list('uuid', flat=True))
    builder = ADXBuilder(get_number_of_family_cube(refDate))
    insuree_data =  builder.create_adx_cube(period, org_units)
    return api.post(
            'dataValueSets',
            xml=insuree_data,
            params={'mergeMode': MergeMode.merge})
    
    
class MonthlySync():
    ## number of insree
    
    refDate = last_day_of_last_month(datetime.datetime.now())
    period = refDate.strftime("%YW%m")
    response = post_insuree_adx(refDate, period)
    response = post_family_size_adx(refDate, period)
    
    


