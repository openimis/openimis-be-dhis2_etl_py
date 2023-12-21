from django.db.models import Q, F, Sum, Count, Max
from django.db.models.functions import Coalesce
from core import filter_validity
from claim.models import ClaimItem, ClaimService
from contribution.models import Premium
from dhis2_etl.models.adx.definition import ADXMappingDataValueDefinition
from dhis2_etl.services.adx.categories import get_age_range_from_boundaries_categories, get_sex_categories, \
    get_payment_state_categories, get_payment_status_categories, get_product_categories, \
    get_claim_status_categories, get_claim_type_categories, get_product_categories, \
    get_claim_details_status_categories, get_main_icd_categories, get_claim_service_categories
from dhis2_etl.services.adx.utils import filter_period, get_location_filter, get_qs_count, get_qs_sum, \
    get_claim_details_period_filter, get_claim_period_filter, get_contribution_period_filter
from insuree.models import Insuree


def get_location_insuree_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_INSUREES",
        period_filter_func=None,
        dataset_from_orgunit_func=lambda l: Insuree.objects.filter(
            *filter_validity(validity=period.from_date), # *filter_validity(validity = period.from_date) is too restrictive
            family__location__parent=l),
        aggregation_func=Count('id'),
        categories=[
            get_age_range_from_boundaries_categories(period),
            get_sex_categories()
        ]
    )


def get_location_family_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_FAMILY",
        period_filter_func=None,
        dataset_from_orgunit_func=lambda l: Insuree.objects.filter(
            head=True, 
            *filter_validity(validity=period.from_date), 
            family__location__parent=l).annotate(policy_value_sum=Sum('family__policies__value')),
        aggregation_func=Count('id'),
        categories=[
            get_age_range_from_boundaries_categories(period),
            get_sex_categories(),
            get_payment_status_categories(period),
            get_payment_state_categories()
        ]
    )


def get_location_contribution_sum_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="SUM_CONTRIBUTIONS",
        period_filter_func=get_contribution_period_filter,
        dataset_from_orgunit_func=lambda l: Premium.objects.filter(
            *filter_validity(), 
            policy__family__location__parent=l),
        aggregation_func= Sum('amount'),
        categories=[get_product_categories(period, prefix = 'policy__product__')]
    )


def get_hf_claim_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM",
        period_filter_func=get_claim_period_filter,
        dataset_from_orgunit_func=lambda hf: hf.claim_set.filter(*filter_validity()).annotate(product_code= Coalesce(Max('services__policy__product__code'),Max('items__policy__product__code'))),
        aggregation_func=Count('id'),
        categories=[
            get_product_categories(period, prefix='product_'),
            get_claim_status_categories(),
            get_claim_type_categories(),
            get_sex_categories(prefix='insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='insuree__'),
        ]
    )


def get_hf_claim_item_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM_ITEM",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimItem.objects.filter(
            claim__health_facility=hf,
            *filter_validity(),
            *filter_validity(prefix='claim__')).annotate(qty=Coalesce('qty_approved', 'qty_provided')),
        aggregation_func=Sum( 'qty'),
        categories=[
            get_product_categories(period),
            get_claim_status_categories(prefix='claim__'),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
        ]
    )


def get_hf_claim_service_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM_SERVICE",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, 
            *filter_validity(),
            qty_provided__gte=0,
            *filter_validity(prefix='claim__')).annotate(qty=Coalesce('qty_approved', 'qty_provided')),
        aggregation_func=Sum('qty'),
        categories=[
            get_product_categories(period),
            get_claim_status_categories(prefix='claim__'),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
        ]
    )
    
def get_hf_claim_service_number_icd_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM_SERVICE_ICD",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, 
            *filter_validity(),
            qty_provided__gte=0.0,

            *filter_validity(prefix='claim__')).annotate(qty=Coalesce('qty_approved', 'qty_provided')),
        aggregation_func=Sum('qty'),
        categories=[
            get_product_categories(period),
            get_claim_status_categories(prefix='claim__'),
            get_claim_details_status_categories(),
            get_main_icd_categories(period, prefix='claim__')
        ]
    )

def get_hf_claim_services_valuated_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="SUM_VALUATED_SERVICE",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, 
            *filter_validity(), price_asked__gte=0.0,qty_provided__gte=0,
            *filter_validity(prefix='claim__'),
            claim__date_processed__isnull=True),
        aggregation_func=Sum('price_valuated'),
        categories=[
            get_product_categories(period),
            get_claim_status_categories(prefix='claim__'),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )


def get_hf_claim_service_asked_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="SUM_ASKED_SERVICE",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, 
            *filter_validity(), 
            price_asked__gte=0.0,
            *filter_validity(prefix='claim__'),
            qty_provided__gte=0 ).annotate(full_price=F('price_asked') * F('qty_provided')),
        aggregation_func=Sum('full_price'),
        categories=[
            get_product_categories(period),
            get_claim_status_categories(prefix='claim__'),
            get_claim_service_categories(),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )

    
 
 