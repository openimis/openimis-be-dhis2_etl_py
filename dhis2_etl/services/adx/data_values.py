from django.db.models import Q, F
from django.db.models.functions import Coalesce

from claim.models import ClaimItem, ClaimService
from contribution.models import Premium
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingDataValueDefinition
from dhis2_etl.services.adx.categories import get_age_range_from_boundaries_categories, get_sex_categories, \
    get_payment_state_categories, get_payment_status_categories, get_policy_product_categories, \
    get_claim_status_categories, get_claim_type_categories, get_claim_product_categories, \
    get_claim_details_status_categories, get_main_icd_categories
from dhis2_etl.services.adx.utils import filter_period, get_location_filter, get_qs_count, get_qs_sum, \
    get_claim_details_period_filter, get_claim_period_filter, get_contribution_period_filter
from insuree.models import Insuree


def get_location_insuree_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_INSUREES",
        period_filter_func=filter_period,
        dataset_from_orgunit_func=lambda l: Insuree.objects.filter(
            validity_to__isnull=True, **get_location_filter(l, 'family__location')),
        aggregation_func=get_qs_count,
        categories=[
            get_age_range_from_boundaries_categories(period),
            get_sex_categories()
        ]
    )


def get_location_family_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_FAMILY",
        period_filter_func=filter_period,
        dataset_from_orgunit_func=lambda l: Insuree.objects.filter(
            head=True, validity_to__isnull=True, **get_location_filter(l, 'family__location')),
        aggregation_func=get_qs_count,
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
        dataset_from_orgunit_func=lambda l: Premium.objects.filter(validity_to__isnull=True).filter(
            policy__family__location=l),
        aggregation_func=lambda qs: get_qs_sum(qs, 'amount'),
        categories=[get_policy_product_categories(period)]
    )


def get_hf_claim_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM",
        period_filter_func=get_claim_period_filter,
        dataset_from_orgunit_func=lambda hf: hf.claim_set.filter(validity_to__isnull=True).filter(
            date_processed__isnull=False),
        aggregation_func=get_qs_count,
        categories=[
            get_claim_product_categories(period),
            get_claim_status_categories(),
            get_claim_type_categories(),
            get_sex_categories(prefix='insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='insuree__'),
            #get_main_icd_categories(period)
        ]
    )


def get_hf_claim_item_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM_ITEM",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimItem.objects.filter(
            claim__health_facility=hf, validity_to__isnull=True, claim__date_processed__isnull=False),
        aggregation_func=lambda qs: get_qs_sum(qs.annotate(qty=Coalesce('qty_approved', 'qty_provided')), 'qty'),
        categories=[
            get_policy_product_categories(period),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )


def get_hf_claim_service_number_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_CLAIM_SERVICE",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, validity_to__isnull=True, claim__date_processed__isnull=False),
        aggregation_func=lambda qs: get_qs_sum(qs.annotate(qty=Coalesce('qty_approved', 'qty_provided')), 'qty'),
        categories=[
            get_policy_product_categories(period),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )


def get_hf_claim_benefits_valuated_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="NB_BENEFIT",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, validity_to__isnull=True, claim__date_processed__isnull=False),
        aggregation_func=lambda qs: get_qs_sum(qs.annotate(qty=Coalesce('qty_approved', 'qty_provided')), 'qty'),
        categories=[
            get_policy_product_categories(period),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )


def get_hf_claim_benefits_asked_dv(period):
    return ADXMappingDataValueDefinition(
        data_element="SUM_ASKED_BENEFIT",
        period_filter_func=get_claim_details_period_filter,
        dataset_from_orgunit_func=lambda hf: ClaimService.objects.filter(
            claim__health_facility=hf, validity_to__isnull=True, claim__date_processed__isnull=False),
        aggregation_func=lambda qs: get_qs_sum(qs.annotate(full_price=F('price_asked') * F('qty_provided')),
                                               'full_price'),
        categories=[
            get_policy_product_categories(period),
            get_claim_details_status_categories(),
            get_claim_type_categories(prefix='claim__'),
            get_sex_categories(prefix='claim__insuree__'),
            get_age_range_from_boundaries_categories(period, prefix='claim__insuree__'),
            #get_main_icd_categories(period, prefix='claim__')
        ]
    )
