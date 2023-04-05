import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q

from claim.models import Claim
from dhis2_etl.adx_transform.adx_models.adx_data import Period
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXCategoryOptionDefinition, ADXMappingCategoryDefinition
from dhis2_etl.services.adx.utils import filter_with_prefix, valid_policy, get_fully_paid, get_partially_paid, not_paid
from medical.models import Diagnosis
from policy.models import Policy
from product.models import Product

# 0-5 ans, 6-12 ans, 13-18 ans, 19-25 ans, 26-35 ans, 36-55 ans, 56-75 ans, 75+
AGE_BOUNDARIES = [6, 13, 19, 26, 36, 56, 76]


def get_age_range_from_boundaries_categories(period, prefix='') -> ADXMappingCategoryDefinition:
    slices = []
    last_age_boundaries = 0
    for age_boundary in AGE_BOUNDARIES:
        # born before
        end_date = period.to_date - relativedelta(years=last_age_boundaries)
        start_date = datetime.datetime.now() - relativedelta(years=age_boundary) + datetime.timedelta(days=1)
        slices.append(ADXCategoryOptionDefinition(
            code=str(last_age_boundaries) + "-" + str(age_boundary - 1),
            filter=lambda qs: filter_with_prefix(qs, 'dob__range', [start_date, end_date], prefix)))
        last_age_boundaries = age_boundary
    end_date = period.to_date - relativedelta(years=last_age_boundaries)
    slices.append(ADXCategoryOptionDefinition(
        code=str(last_age_boundaries) + "+",
        filter=lambda qs: filter_with_prefix(qs, 'dob__lt', end_date, prefix)))
    return ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=slices
    )


def get_sex_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", filter=lambda qs: filter_with_prefix(qs, 'gender__code', 'M', prefix)),
            ADXCategoryOptionDefinition(
                code="F", filter=lambda qs: filter_with_prefix(qs, 'gender__code', 'F', prefix))
        ]
    )


def get_payment_status_categories(period) -> ADXMappingCategoryDefinition:
    # Fully paid, partially paid, not paid
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="paid",
                filter=lambda insuree_qs: insuree_qs.annotate(policy_value_sum=Sum('family__policies__value')).filter(
                    valid_policy(period) & get_fully_paid())),
            ADXCategoryOptionDefinition(
                code="partialy-paid",
                filter=lambda insuree_qs: insuree_qs.annotate(policy_value_sum=Sum('family__policies__value')).filter(
                    valid_policy(period) & get_partially_paid())),
            ADXCategoryOptionDefinition(
                code="not-paid",
                filter=lambda insuree_qs: insuree_qs.filter(valid_policy(period) & not_paid())),
        ]
    )


def get_payment_state_categories() -> ADXMappingCategoryDefinition:
    # new renew
    return ADXMappingCategoryDefinition(
        category_name="payment_state",
        category_options=[
            ADXCategoryOptionDefinition(
                code="new", filter=lambda insuree_qs: insuree_qs.filter(Q(family__policies__stage=Policy.STAGE_NEW))),
            ADXCategoryOptionDefinition(
                code="renew",
                filter=lambda insuree_qs: insuree_qs.filter(Q(family__policies__stage=Policy.STAGE_RENEWED))),
        ]
    )


def get_claim_status_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="item_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="approved", filter=lambda qs: filter_with_prefix(qs, 'status', Claim.STATUS_VALUATED, prefix)),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: filter_with_prefix(qs, 'status', Claim.STATUS_REJECTED, prefix)),
        ]
    )


def get_claim_type_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="item_type",
        category_options=[
            ADXCategoryOptionDefinition(
                code="Emergency", filter=lambda qs: filter_with_prefix(qs, 'visit_type', 'E', prefix)),
            ADXCategoryOptionDefinition(
                code="Referrals", filter=lambda qs: filter_with_prefix(qs, 'visit_type', 'R', prefix)),
            ADXCategoryOptionDefinition(
                code="Other", filter=lambda qs: filter_with_prefix(qs, 'visit_type', 'O', prefix)),
        ]
    )


def get_claim_details_status_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="aproved", filter=lambda qs: filter_with_prefix(qs, 'status', Claim.STATUS_VALUATED, prefix)),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: filter_with_prefix(qs, 'status', Claim.STATUS_VALUATED, prefix)),
        ]
    )

def get_main_icd_categories(period, prefix='') -> ADXMappingCategoryDefinition:
    slices = []
    diagnosis = Diagnosis.objects.filter(legacy_id__isnull=True) \
        .filter(validity_from__gte=period.from_date) \
        .filter(validity_from__lte=period.to_date)
    for diagnose in diagnosis:
        slices.append(ADXCategoryOptionDefinition(
            code=str(diagnose.code),
            filter=lambda qs: filter_with_prefix(qs, 'icd', diagnose, prefix)))
    return ADXMappingCategoryDefinition(
        category_name="icd",
        category_options=slices
    )


def get_policy_product_categories(period) -> ADXMappingCategoryDefinition:
    slices = []
    products = Product.objects.filter(legacy_id__isnull=True) \
        .filter(validity_from__gte=period.from_date) \
        .filter(validity_from__lte=period.to_date)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=str(product.code),
            filter=lambda premium_qs: premium_qs.filter(policy__product=product)))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )


def get_claim_product_categories(period: Period) -> ADXMappingCategoryDefinition:
    slices = []
    products = Product.objects.filter(legacy_id__isnull=True) \
        .filter(validity_from__gte=period.from_date) \
        .filter(validity_from__lte=period.to_date)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=str(product.code),
            filter=lambda qs: qs.filter(Q(items__policy__product=product) | Q(services__policy__product=product))))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )
