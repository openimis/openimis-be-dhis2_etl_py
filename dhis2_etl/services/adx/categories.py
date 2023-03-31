import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Exists, OuterRef, Q

from claim.models import Claim
from contribution.models import Premium
from dhis2_etl.adx_transform.adx_models.adx_data import Period
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXCategoryOptionDefinition, ADXMappingCategoryDefinition
from dhis2_etl.services.adx.utils import filter_with_prefix
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


def _get_fully_paid():
    return Q(policy_value_sum__lte=Sum('family__policies__premiums__amount'))


def _get_partially_paid():
    return Q(policy_value_sum__gt=Sum('family__policies__premiums__amount'))


def _not_paid():
    return Exists(Premium.objects.filter(validity_to__isnull=True).filter(policy=OuterRef('family__policies')))


def _valid_policy(period):
    return (Q(family__policies__effective_date__lte=period.to_date)
            & Q(family__policies__expiry_date__lt=period.to_date)) \
        & Q(family__policies__validity_to__isnull=True)


def get_payment_status_categories(period) -> ADXMappingCategoryDefinition:
    # Fully paid, partially paid, not paid
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="paid",
                filter=lambda insuree_qs: insuree_qs.annotate(policy_value_sum=Sum('family__policies__value')).filter(
                    _valid_policy(period) & _get_fully_paid())),
            ADXCategoryOptionDefinition(
                code="partialy-paid",
                filter=lambda insuree_qs: insuree_qs.annotate(policy_value_sum=Sum('family__policies__value')).filter(
                    _valid_policy(period) & _get_partially_paid())),
            ADXCategoryOptionDefinition(
                code="not-paid",
                filter=lambda insuree_qs: insuree_qs.filter(_valid_policy(period) & _not_paid())),
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
                code="aproved", filter=lambda qs: qs.filter(Q('%sstatus' % prefix, Claim.STATUS_VALUATED))),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: qs.filter(Q('%sstatus' % prefix, Claim.STATUS_VALUATED))),
        ]
    )


def get_claim_type_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="item_type",
        category_options=[
            ADXCategoryOptionDefinition(
                code="Emergency", filter=lambda qs: qs.filter(Q('%svisit_type' % prefix, 'E'))),
            ADXCategoryOptionDefinition(
                code="Referrals", filter=lambda qs: qs.filter(Q('%svisit_type' % prefix, 'R'))),
            ADXCategoryOptionDefinition(
                code="Other", filter=lambda qs: qs.filter(Q('%svisit_type' % prefix, 'O'))),
        ]
    )


def get_claim_details_status_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="aproved", filter=lambda qs: qs.filter(Q('%sstatus' % prefix, Claim.STATUS_VALUATED))),
            ADXCategoryOptionDefinition(
                code="rejected", filter=lambda qs: qs.filter(Q('%sstatus' % prefix, Claim.STATUS_VALUATED))),
        ]
    )


def get_main_icd_categories(period, prefix='') -> ADXMappingCategoryDefinition:
    slices = []
    diagnosis = Diagnosis.objects.filter(legacy_id__isnull=True) \
        .filter(validity_from__lte=period.from_date) \
        .filter(validity_from__gte=period.to_date)
    for diagnose in diagnosis:
        slices.append(ADXCategoryOptionDefinition(
            code=str(diagnose.code),
            filter=lambda qs: qs.filter(Q('%sicd' % prefix, diagnosis))))
    return ADXMappingCategoryDefinition(
        category_name="icd",
        category_options=slices
    )


def get_policy_product_categories(period) -> ADXMappingCategoryDefinition:
    slices = []
    products = Product.objects.filter(legacy_id__isnull=True) \
        .filter(validity_from__lte=period.from_date) \
        .filter(validity_from__gte=period.to_date)
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
        .filter(validity_from__lte=period.from_date) \
        .filter(validity_from__gte=period.to_date)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=str(product.code),
            filter=lambda qs: qs.filter(Q(items__policy__product=product) | Q(services__policy__product=product))))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )
