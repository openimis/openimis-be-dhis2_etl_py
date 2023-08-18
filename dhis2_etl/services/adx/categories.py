import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q

from claim.models import Claim
from dhis2_etl.models.adx.data import Period
from dhis2_etl.models.adx.definition import ADXCategoryOptionDefinition, ADXMappingCategoryDefinition
from dhis2_etl.services.adx.utils import filter_with_prefix, q_with_prefix, valid_policy, get_fully_paid, get_partially_paid, not_paid
from medical.models import Diagnosis
from policy.models import Policy
from product.models import Product
from dhis2_etl.utils import clean_code

# 0-5 ans, 6-12 ans, 13-18 ans, 19-25 ans, 26-35 ans, 36-55 ans, 56-75 ans, 75+
AGE_BOUNDARIES = [6, 13, 19, 26, 36, 56, 76]


def get_age_range_from_boundaries_categories(period, prefix='') -> ADXMappingCategoryDefinition:
    slices = []
    range = {}
    last_age_boundaries = 0
    for age_boundary in AGE_BOUNDARIES:
        # born before
        # need to store all range , e.i not update start/stop date because the lambda is evaluated later
        slices.append(ADXCategoryOptionDefinition(
            code=str(last_age_boundaries) + "_" + str(age_boundary - 1),
            name= str(last_age_boundaries) + "-" + str(age_boundary - 1),
            filter= build_age_q( 
                    [
                        (period.to_date - relativedelta(years=age_boundary)).strftime("%Y-%m-%d"),
                        (period.to_date - relativedelta(years=last_age_boundaries)).strftime("%Y-%m-%d"),
                    ] 
                    , prefix)))
        last_age_boundaries = age_boundary
    end_date = period.to_date - relativedelta(years=last_age_boundaries)
    slices.append(ADXCategoryOptionDefinition(
        code=str(last_age_boundaries) + "P",
        name=str(last_age_boundaries) + "p",
        filter=q_with_prefix('dob__lt', end_date.strftime("%Y-%m-%d"), prefix)))
    return ADXMappingCategoryDefinition(
        category_name="ageGroup",
        category_options=slices
    )

def build_age_q(range, prefix ):
    return q_with_prefix('dob__range', range, prefix)

def get_sex_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", name= "Male", filter= q_with_prefix( 'gender__code', 'M', prefix)),
            ADXCategoryOptionDefinition(
                code="F", name= "Female", filter=q_with_prefix( 'gender__code', 'F', prefix))
        ]
    )


def get_payment_status_categories(period) -> ADXMappingCategoryDefinition:
    # Fully paid, partially paid, not paid
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="PAID",
                name= "Paid",
                filter=Q(valid_policy(period) & get_fully_paid())),
            ADXCategoryOptionDefinition(
                code="NOT_PAID",
                name= "Not paid",
                filter=Q(valid_policy(period) & not_paid())),
            ADXCategoryOptionDefinition(
                code="PARTIALY_PAID",
                name= "Partialy paid",
                filter=Q(valid_policy(period) & get_partially_paid())),
            ADXCategoryOptionDefinition(
                code="NO_POLICY",
                name= "No policy",
                filter=Q(family__policies__isnull=True)),
        ]
    )


def get_payment_state_categories() -> ADXMappingCategoryDefinition:
    # new renew
    return ADXMappingCategoryDefinition(
        category_name="payment_state",
        category_options=[
            ADXCategoryOptionDefinition(
                name = "New",
                code="NEW", filter=Q(family__policies__stage=Policy.STAGE_NEW)),
            ADXCategoryOptionDefinition(
                name = "Renew",code="RENEW",
                filter=Q(family__policies__stage=Policy.STAGE_RENEWED)),
            ADXCategoryOptionDefinition(
                name = "No-policy",code="NO_POLICY",
                filter=Q(family__policies__isnull=True)),
        ]
    )


def get_claim_status_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="item_status",
        category_options=[
            ADXCategoryOptionDefinition(
                name = "Approved", code="APPROVED", filter=q_with_prefix( 'status', Claim.STATUS_VALUATED, prefix)),
            ADXCategoryOptionDefinition(
                name = "Rejected",code="REJECTED", filter=q_with_prefix( 'status', Claim.STATUS_REJECTED, prefix)),
            ADXCategoryOptionDefinition(
                name = "checked",code="CHECKED", filter=q_with_prefix( 'status', Claim.STATUS_CHECKED, prefix)),
            ADXCategoryOptionDefinition(
                name = "Processed",code="PROCESSED", filter=q_with_prefix( 'status', Claim.STATUS_PROCESSED, prefix)),
        ]
    )


def get_claim_type_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="item_type",
        category_options=[
            ADXCategoryOptionDefinition(
                name = "Emergency",code="EMERGENCY", filter=q_with_prefix( 'visit_type', 'E', prefix)),
            ADXCategoryOptionDefinition(
                name = "Referrals",code="REFERRALS", filter=q_with_prefix( 'visit_type', 'R', prefix)),
            ADXCategoryOptionDefinition(
                name = "Other",code="OTHER", filter=q_with_prefix( 'visit_type', 'O', prefix)),
        ]
    )


def get_claim_details_status_categories(prefix='') -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_status",
        category_options=[
            ADXCategoryOptionDefinition(
               name = "Approved", code="APPROVED", filter=q_with_prefix( 'status', Claim.STATUS_VALUATED, prefix)),
            ADXCategoryOptionDefinition(
                name = "Rejected",code="REJECTED", filter=q_with_prefix( 'status', Claim.STATUS_VALUATED, prefix)),
             ADXCategoryOptionDefinition(
                name = "not assessed",code="NOT_ASSESSED", filter=q_with_prefix( 'status__isnull', True, prefix)),
        ]
    )

def get_main_icd_categories(period, prefix='') -> ADXMappingCategoryDefinition:
    slices = []
    diagnosis = Diagnosis.objects.filter(validity_to__isnull=True)
    for diagnose in diagnosis:
        slices.append(ADXCategoryOptionDefinition(
            code=clean_code(str(diagnose.code)),
            name=str(diagnose.code),
            filter=q_with_prefix( 'icd', diagnose, prefix)))
    return ADXMappingCategoryDefinition(
        category_name="icd",
        category_options=slices
    )


def get_policy_product_categories(period) -> ADXMappingCategoryDefinition:
    slices = []
    products = Product.objects.filter(validity_to__isnull=True)
    for product in products:
        slices.append(ADXCategoryOptionDefinition(
            code=clean_code(str(product.code)),
            name=f"{product.code}-{product.name}",
            filter=Q(policy__product=product)))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )


def get_claim_product_categories(period: Period) -> ADXMappingCategoryDefinition:
    slices = []
    products = Product.objects.filter(validity_to__isnull=True)
    for product in products:
        name = f"{product.code}-{product.name}"
        slices.append(ADXCategoryOptionDefinition(
            code=clean_code(str(product.code)),
            name=name,
            filter=Q(Q(items__policy__product=product) | Q(services__policy__product=product))))
    return ADXMappingCategoryDefinition(
        category_name="product",
        category_options=slices
    )
