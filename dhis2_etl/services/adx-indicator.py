import datetime
from dateutil.relativedelta import relativedelta
from dhis2 import api

from django.db.models import Q, Sum,OuterRef, Exists, F
from django.db.models.functions import  Coalesce
from dataclasses import asdict
from typing import List
from xml.etree import ElementTree

from django.test import TestCase
from location.models import HealthFacility, Location
from product.models import Product
from contribution.models import Premium
from claim.models import Claim, ClaimDetail
from medical.models import Diagnosis

from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.adx_transform.builders import ADXBuilder
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingDataValueDefinition, \
    ADXMappingCategoryDefinition, ADXCategoryOptionDefinition, ADXMappingCubeDefinition, ADXMappingGroupDefinition
from dhis2_etl.utils import build_dhis2_id

from policy.models import STAGE_RENEW, STAGE_NEW
from dhis2_etl.adx_transform.adx_models.adx_time_period import ISOFormatPeriodType, PeriodParsingException

from ..models.dhis2Enum import ImportStrategy, MergeMode

#0-5 ans, 6-12 ans, 13-18 ans, 19-25 ans, 26-35 ans, 36-55 ans, 56-75 ans, 75+
AGE_BOUNDARIES = [6,13,19,26,36,56,76]

def get_age_range_from_boundaries_categories(age_boundaries, period, prefix = ''):
    slices = []
    last_age_boundaries = 0
    for age_boundary in age_boundaries:
        #born before 
        end_date =  period.to_date-relativedelta(years=last_age_boundaries)
        start_date =  datetime.datetime.now() -relativedelta(years=age_boundary)+datetime.timedelta(days=1)
        slices.append(ADXCategoryOptionDefinition(
            code=str(last_age_boundaries)+"-"+str(age_boundary-1),
            filter=lambda insuree_qs: insuree_qs.filter(Q('%sdob__range' % prefix,(start_date, end_date)))))
        last_age_boundaries = age_boundary
    end_date =  period.to_date-relativedelta(years=last_age_boundaries)    
    slices.append(ADXCategoryOptionDefinition(
            code=str(last_age_boundaries)+"+",
            filter=lambda insuree_qs: insuree_qs.filter(Q('%sdob__lt' % prefix, end_date))))
    return ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=slices
    )    

        
def get_sex_categories(prefix = ''):
    return  ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", filter=lambda insuree_qs: insuree_qs.filter(Q('%sgender__code' % prefix , 'M'))),
            ADXCategoryOptionDefinition(
                code="F", filter=lambda insuree_qs: insuree_qs.filter(Q('%sgender__code' % prefix , 'F')))
        ]
    )
def get_valid_policy_filter(period):
    return (Q(family__policies__effective_date__lte= period.to_date)\
            & Q(family__policies__expiry_date__lt= period.to_date))\
            & Q(family__policies__validity_to__isnull=True)
def get_fully_payed():
    return Q(family__policies__value__lte = Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')).aggregate(sum=Sum('amount'))['sum'])
def get_partialy_payed():
    return Q(family__policies__medicalvalue__gt = Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')).aggregate(sum=Sum('amount'))['sum'])
def not_payed():
    return Exists(Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')))
    

# Fully payed, partially payed, not payed
def get_payment_status_categories(period):
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(period) & get_fully_payed())),
            ADXCategoryOptionDefinition(
                code="partialy-payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(period) & get_partialy_payed())),
            ADXCategoryOptionDefinition(
                code="not-payed", filter=lambda insuree_qs: insuree_qs.filter(get_valid_policy_filter(period) & not_payed())),
        ]
    )
# new renew
def get_payment_state_categories(period):
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="new", filter=lambda insuree_qs: insuree_qs.filter(Q(family__policies__stage =  STAGE_NEW ))),
            ADXCategoryOptionDefinition(
                code="renew", filter=lambda insuree_qs: insuree_qs.filter(Q(family__policies__stage =  STAGE_RENEW ))),
        ]
    )
    
def get_number_insuree_group(period):
    return ADXMappingGroupDefinition(
                comment="number of family per location",
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_INSUREES",
                        #period_filter_func = _filter_period,
                        dataset_from_orgunit_func=lambda l: l.insuree_set.filter(validity_to__isnull=True),
                        aggregation_func=lambda insuress_qs: str(insuress_qs.count()),
                        categories=[
                            get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period),
                            get_sex_categories()
                        ]
                    )
                ]
            )
    
def get_number_family_group(period):
    return ADXMappingGroupDefinition(
                comment="number of family per location",
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="NB_FAMILY",
                        #period_filter_func = _filter_period,
                        dataset_from_orgunit_func=lambda l: l.insuree_set.filter(head=True).filter(validity_to__isnull=True),
                        aggregation_func=lambda family_qs: str(family_qs.count()),
                        categories=[
                            get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period),
                            get_sex_categories(),
                            get_payment_status_categories(period),
                            get_payment_state_categories(period)
                        ]
                    )
                ]
            )
    
def get_amount_contribution_group(period_obj):    
    return ADXMappingGroupDefinition(
                comment="Contribution amount per location of product",
                data_values=[
                    ADXMappingDataValueDefinition(
                        data_element="SUM_CONTRIBUTIONS",
                        period_filter_func = lambda qs, period: qs.filter(pay_date__range=[period.from_date, period.to_date]),
                        dataset_from_orgunit_func=lambda l:  Premium.objects.filter(validity_to__isnull=True)\
                            .filter(policy__familly__head__location=l),
                        aggregation_func=lambda contribution_qs: str(contribution_qs.sum('amount')),
                        categories=[get_policy_product_categories(period_obj)]
                    )
                ]
            )

def get_main_icd_categories(period, prefix = ''):
    slices = []
    diagnosis = Diagnosis.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=period.from_date)\
        .filter(validity_from__gte=period.to_date)
    for diagnose in diagnosis:
        slices.append(ADXCategoryOptionDefinition(
            code=str(diagnose.code),
            filter=lambda qs: qs.filter(Q('%sicd' % prefix, diagnosis ))))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )
    
def get_enrollment_cube(period):
    period_type = ISOFormatPeriodType()
    period_obj = period_type.build_period(period)
    return ADXMappingCubeDefinition(
        name='Enrolment',
        to_org_unit_code_func= lambda l: build_dhis2_id(l.uuid),
        period_type=period_type,
        groups=[
            get_number_insuree_group(period_obj),            
            get_number_family_group(period_obj),
            get_amount_contribution_group( period_obj)
        ]
    )

def _claim_period_filter(qs,period):
    return qs.filter((Q(date_to__isnull=True) & Q(date_from__range=[period.from_date, period.to_date])) | (Q(date_to__isnull=False) & Q(date_to__range=[period.from_date, period.to_date])))

def _claim_details_period_filter(qs,period):
    return qs.filter((Q(claim__date_to__isnull=True) & Q(claim__date_from__range=[period.from_date, period.to_date])) | (Q(claim__date_to__isnull=False) & Q(claim__date_to__range=[period.from_date, period.to_date])))

def get_claim_status_categoroies(prefix = ''):
    return ADXMappingCategoryDefinition(
        category_name="item_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="aproved", filter=lambda qs: qs.filter(Q('%sstatus' % prefix , Claim.STATUS_VALUATED) )),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: qs.filter(Q('%sstatus' % prefix , Claim.STATUS_VALUATED) )),
        ]
    )

def get_claim_type_categoroies(prefix = ''):
    return ADXMappingCategoryDefinition(
        category_name="item_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="Emergency", filter=lambda qs: qs.filter(Q('%visit_type' % prefix , 'E') ) ),
            ADXCategoryOptionDefinition(
                code="Referrals", filter=lambda qs: qs.filter(Q('%visit_type' % prefix , 'R'))),
            ADXCategoryOptionDefinition(
                code="Other", filter=lambda qs: qs.filter(Q('%visit_type' % prefix , 'O'))),
        ]
    )

def get_claim_details_status_categoroies(prefix = ''):
    return ADXMappingCategoryDefinition(
        category_name="claim_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="aproved", filter=lambda qs: qs.filter(Q('%sstatus' % prefix , ClaimDetail.STATUS_VALUATED) )),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: qs.filter(Q('%sstatus' % prefix , ClaimDetail.STATUS_VALUATED) )),
        ]
    )
    
def get_number_claim_group(period_obj):
    return ADXMappingGroupDefinition(
            comment="number of claim per HF",
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element="NB_CLAIM",
                    period_filter_func =_claim_period_filter ,
                    dataset_from_orgunit_func=lambda l:  l.claim_set.filter(validity_to__isnull=True).filter(date_processed__isnull=False),
                    aggregation_func=lambda qs: str(qs.count()),
                    categories=[
                        get_claim_product_categories(period_obj),
                        get_claim_status_categoroies(),
                        get_claim_type_categoroies(),
                        get_sex_categories(prefix = 'insuree'),
                        get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period_obj, prefix = 'insuree')
                    ]
                )
            ]
        )

def get_number_benefit_group(period_obj):
    return ADXMappingGroupDefinition(
            comment="number of benefit per HF",
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element="NB_BENEFIT",
                    period_filter_func =_claim_details_period_filter ,
                    dataset_from_orgunit_func=lambda l:  l.claim_set.items.filter(validity_to__isnull=True).filter(claim__date_processed__isnull=False),
                    aggregation_func=lambda qs: str(qs.aggregate(sum=Coalesce('qty_approved','qty_provided'))),
                    categories=[
                        get_policy_product_categories(period_obj),
                        get_claim_details_status_categoroies(),
                        get_claim_type_categoroies(prefix = 'claim__'),
                        get_sex_categories(prefix = 'claim__insuree'),
                        get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period_obj, prefix = 'claim__insuree'),
                        get_main_icd_categories(period_obj,)
                    ]
                )
            ]
        )

def get_amount_benefit_valuated_group(period_obj):
    return ADXMappingGroupDefinition(
            comment="number of claim per HF",
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element="SUM_APPROUVED_BENEFIT",
                    period_filter_func =_claim_details_period_filter ,
                    dataset_from_orgunit_func=lambda l:  l.claim_set.services.filter(validity_to__isnull=True).filter(claim__date_processed__isnull=False),
                    #takes Qty and price into account
                    aggregation_func=lambda contribution_qs: str(contribution_qs.sum('price_valuated')),
                    categories=[
                        get_policy_product_categories(period_obj),
                        get_claim_details_status_categoroies(),
                        get_claim_type_categoroies(prefix = 'claim__'),
                        get_sex_categories(prefix = 'claim__insuree'),
                        get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period_obj, prefix = 'claim__insuree'),
                        get_main_icd_categories(period_obj, prefix = 'claim__')
                    ]
                )
            ]
        )

def get_amount_benefit_asked_group(period_obj):
    return ADXMappingGroupDefinition(
            comment="number of claim per HF",
            data_values=[
                ADXMappingDataValueDefinition(
                    data_element="SUM_ASKED_BENEFIT",
                    period_filter_func =_claim_details_period_filter ,
                    dataset_from_orgunit_func=lambda l:  l.claim_set.services.filter(validity_to__isnull=True).filter(claim__date_processed__isnull=False),
                    aggregation_func=lambda contribution_qs: str(contribution_qs.aggregate(sum=Sum(F('price_asked')*F('qty_provided')))),
                    categories=[
                        get_policy_product_categories(period_obj),
                        get_claim_details_status_categoroies(),
                        get_claim_type_categoroies(prefix = 'claim__'),
                        get_sex_categories(prefix = 'claim__insuree'),
                        get_age_range_from_boundaries_categories(AGE_BOUNDARIES,period_obj, prefix = 'claim__insuree'),
                        get_main_icd_categories(period_obj, prefix = 'claim__')
                    ]
                )
            ]
        )


def get_claim_cube(period):
    period_type = ISOFormatPeriodType()
    period_obj = period_type.build_period(period)
    return ADXMappingCubeDefinition(
        name='PROCESSED_CLAIM',
        period_type=period_type,
        to_org_unit_code_func= lambda l: build_dhis2_id(l.uuid),
        groups=[
            get_number_claim_group(period_obj),
            get_number_benefit_group(period_obj),
            get_amount_benefit_valuated_group(period_obj),
            get_amount_benefit_asked_group(period_obj)
        ]
    )
    
def get_policy_product_categories(period_obj):
    slices = []
    products = Product.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=period_obj.from_date)\
        .filter(validity_from__gte=period_obj.to_date)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=str(product.code),
            filter=lambda premium_qs: premium_qs.filter(policy__product= product)))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )

def get_claim_product_categories(period_obj):
    slices = []
    products = Product.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=period_obj.from_date)\
        .filter(validity_from__gte=period_obj.to_date)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=str(product.code),
            filter=lambda qs: qs.filter(Q(items__policy__product= product) | Q(services__policy__product= product))))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )

def last_day_of_last_month(any_day):
    return any_day - datetime.timedelta(days=any_day.day)

#Nombre d’adhérents par district, par municipalité, par sexe, par âge 
def post_enrollment_cube(period):
    org_units =  list(Location.all().filter(validity_to__isnull = True).filter(type = 'V'))
    builder = ADXBuilder(get_enrollment_cube(period))
    insuree_data =  builder.create_adx_cube(period, org_units)
    return api.post(
            'dataValueSets',
            xml=insuree_data,
            params={'mergeMode': MergeMode.merge})

#Nombre dde claim/benefices
def post_enrollment_cube(period):
    org_units =  list(HealthFacility.all().filter(validity_to__isnull = True))
    builder = ADXBuilder(get_claim_cube(period))
    insuree_data =  builder.create_adx_cube(period, org_units)
    return api.post(
            'dataValueSets',
            xml=insuree_data,
            params={'mergeMode': MergeMode.merge})

class MonthlySync():
    ## number of insree
    
    refDate = last_day_of_last_month(datetime.datetime.now())
    period = refDate.strftime("%YW%m")
    response = post_enrollment_cube(period)

    


