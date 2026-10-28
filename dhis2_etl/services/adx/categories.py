import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q, Max

from claim.models import Claim, ClaimDetail
from dhis2_etl.configurations import GeneralConfiguration
from django_adx.models.adx.data import Period
from django_adx.models.adx.definition import (
    ADXCategoryOptionDefinition,
    ADXMappingCategoryDefinition,
)
from dhis2_etl.services.adx.utils import (
    filter_with_prefix,
    q_with_prefix,
    get_period_last_day,
    valid_policy,
    get_fully_paid,
    get_partially_paid,
    not_paid,
)
from medical.models import Diagnosis, Service
from policy.models import Policy
from product.models import Product
from dhis2_etl.utils import clean_code
from dict2obj import Dict2Obj

adx = Dict2Obj(GeneralConfiguration.get_adx())
AGE_BOUNDARIES = adx.age_disaggregation
VALUE_BOUNDARIES = adx.value_disaggregation

NONE_OPT = ADXCategoryOptionDefinition(code="NONE", name="None", is_default=True)


def get_age_range_from_boundaries_categories(
    period, prefix=""
) -> ADXMappingCategoryDefinition:
    # age reached on the last day of the period
    last_day = get_period_last_day(period)
    slices = []
    last_age_boundary = 0
    for age_boundary in AGE_BOUNDARIES:
        slice_code = f"P{last_age_boundary}Y-P{age_boundary - 1}Y"
        # dates are computed now because the filters are evaluated later
        slices.append(
            ADXCategoryOptionDefinition(
                code=slice_code,
                name=slice_code,
                filter=Q(
                    **{
                        f"{prefix}dob__gt": (
                            last_day - relativedelta(years=age_boundary)
                        ).strftime("%Y-%m-%d"),
                        f"{prefix}dob__lte": (
                            last_day - relativedelta(years=last_age_boundary)
                        ).strftime("%Y-%m-%d"),
                    }
                ),
            )
        )
        last_age_boundary = age_boundary
    end_date = last_day - relativedelta(years=last_age_boundary)
    slice_code = f"P{last_age_boundary}Y-P9999Y"

    slices.append(
        ADXCategoryOptionDefinition(
            code=slice_code,
            name=slice_code,
            filter=q_with_prefix("dob__lte", end_date.strftime("%Y-%m-%d"), prefix),
        )
    )
    return ADXMappingCategoryDefinition(
        category_name="ageGroup", category_options=slices
    )


def get_value_range_from_boundaries_categories(path):
    first_boundary = VALUE_BOUNDARIES[0]
    slices = [
        ADXCategoryOptionDefinition(
            code=f"V{first_boundary}-",
            name=f"V{first_boundary}-",
            filter=q_with_prefix("__lt", first_boundary, path),
        )
    ]
    for low, high in zip(VALUE_BOUNDARIES, VALUE_BOUNDARIES[1:]):
        slice_code = f"V{low}-V{high}"
        slices.append(
            ADXCategoryOptionDefinition(
                code=slice_code,
                name=slice_code,
                filter=Q(**{f"{path}__gte": low, f"{path}__lt": high}),
            )
        )
    last_boundary = VALUE_BOUNDARIES[-1]
    slices.append(
        ADXCategoryOptionDefinition(
            code=f"V{last_boundary}+",
            name=f"V{last_boundary}+",
            filter=q_with_prefix("__gte", last_boundary, path),
        )
    )
    return ADXMappingCategoryDefinition(
        category_name="valueGroup", category_options=slices
    )


def build_age_q(range, prefix):
    return q_with_prefix("dob__range", range, prefix)


def get_sex_categories(prefix="") -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="sex",
        category_options=[
            ADXCategoryOptionDefinition(
                code="M", name="MALE", filter=q_with_prefix("gender__code", "M", prefix)
            ),
            ADXCategoryOptionDefinition(
                code="F",
                name="FEMALE",
                filter=q_with_prefix("gender__code", "F", prefix),
            ),
            ADXCategoryOptionDefinition(code="O", name="OTHER", is_default=True),
        ],
    )


def get_payment_status_categories(period) -> ADXMappingCategoryDefinition:
    # Fully paid, partially paid, not paid
    return ADXMappingCategoryDefinition(
        category_name="payment_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code="PAID",
                name="Paid",
                filter=Q(valid_policy(period) & get_fully_paid()),
            ),
            ADXCategoryOptionDefinition(
                code="NOT_PAID",
                name="Not paid",
                filter=Q(
                    valid_policy(period) & ~get_fully_paid() & ~get_partially_paid()
                ),
            ),
            ADXCategoryOptionDefinition(
                code="PARTIALY_PAID",
                name="Partialy paid",
                filter=Q(valid_policy(period) & get_partially_paid()),
            ),
            ADXCategoryOptionDefinition(
                code="NO_POLICY", name="No policy", is_default=True
            ),
        ],
    )


def get_payment_state_categories() -> ADXMappingCategoryDefinition:
    # new renew
    return ADXMappingCategoryDefinition(
        category_name="payment_state",
        category_options=[
            ADXCategoryOptionDefinition(
                name="New",
                code="NEW",
                filter=Q(family__policies__stage=Policy.STAGE_NEW),
            ),
            ADXCategoryOptionDefinition(
                name="Renew",
                code="RENEW",
                filter=Q(family__policies__stage=Policy.STAGE_RENEWED),
            ),
            ADXCategoryOptionDefinition(
                name="No-policy", code="NO_POLICY", is_default=True
            ),
        ],
    )


def get_policy_status_categories() -> ADXMappingCategoryDefinition:
    # expects the queryset to be annotated with get_policy_status_annotation
    # option codes are prefixed to avoid sharing options with payment categories
    return ADXMappingCategoryDefinition(
        category_name="policy_status",
        category_options=[
            ADXCategoryOptionDefinition(
                code=f"POL_{status}",
                name=status.capitalize(),
                filter=Q(policy_status=status),
            )
            for status in ["ACTIVE", "SUSPENDED", "IDLE", "READY", "EXPIRED"]
        ]
        + [
            ADXCategoryOptionDefinition(
                code="POL_NONE", name="No policy", is_default=True
            ),
        ],
    )


def get_claim_status_categories(prefix="") -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_status",
        category_options=[
            ADXCategoryOptionDefinition(
                name="Approved",
                code="APPROVED",
                filter=q_with_prefix("status", Claim.STATUS_VALUATED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Rejected",
                code="REJECTED",
                filter=q_with_prefix("status", Claim.STATUS_REJECTED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Checked",
                code="CHECKED",
                filter=q_with_prefix("status", Claim.STATUS_CHECKED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Processed",
                code="PROCESSED",
                filter=q_with_prefix("status", Claim.STATUS_PROCESSED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Entered", code="ENTERED", is_default=True
            ),
        ],
    )


def get_claim_type_categories(prefix="") -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_type",
        category_options=[
            ADXCategoryOptionDefinition(
                name="Emergency",
                code="EMERGENCY",
                filter=q_with_prefix("visit_type", "E", prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Referrals",
                code="REFERRALS",
                filter=q_with_prefix("visit_type", "R", prefix),
            ),
            ADXCategoryOptionDefinition(name="Other", code="OTHER", is_default=True),
        ],
    )


def get_claim_service_categories(prefix="") -> ADXMappingCategoryDefinition:
    slices = [NONE_OPT]
    slice_codes = []
    services = Service.objects.all().order_by("-validity_to")
    for service in services:
        cleaned_code = clean_code(str(service.code))
        # to avoid twice the same code
        if cleaned_code not in slice_codes:
            slice_codes.append(cleaned_code)
            slices.append(
                ADXCategoryOptionDefinition(
                    code=cleaned_code,
                    name=(
                        f"{service.code}-{service.name}"
                        if not service.name.startswith(service.code)
                        else service.name
                    ),
                    filter=None,
                )
            )

    return ADXMappingCategoryDefinition(
        category_name="claim_service",
        category_options=slices,
        path=f"{prefix}service__code",
    )


def get_claim_details_status_categories(prefix="") -> ADXMappingCategoryDefinition:
    return ADXMappingCategoryDefinition(
        category_name="claim_detail_status",
        category_options=[
            ADXCategoryOptionDefinition(
                name="Approved",
                code="APPROVED",
                filter=q_with_prefix("status", ClaimDetail.STATUS_PASSED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="Rejected",
                code="REJECTED",
                filter=q_with_prefix("status", ClaimDetail.STATUS_REJECTED, prefix),
            ),
            ADXCategoryOptionDefinition(
                name="not assessed", code="NOT_ASSESSED", is_default=True
            ),
        ],
    )


def get_main_icd_categories(period, prefix="") -> ADXMappingCategoryDefinition:
    slices = [NONE_OPT]
    slice_codes = []
    diagnosis = Diagnosis.objects.all().order_by("-validity_to")
    for diagnose in diagnosis:
        cleaned_code = clean_code(str(diagnose.code))
        # to avoid twice the same code
        if cleaned_code not in slice_codes:
            slice_codes.append(cleaned_code)
            slices.append(
                ADXCategoryOptionDefinition(
                    code=cleaned_code,
                    name=(
                        f"{diagnose.code}-{diagnose.name}"
                        if not diagnose.name.startswith(diagnose.code)
                        else diagnose.name
                    ),
                    filter=None,
                )
            )

    return ADXMappingCategoryDefinition(
        category_name="icd", category_options=slices, path=f"{prefix}icd__code"
    )


def get_product_categories(period, prefix="product__") -> ADXMappingCategoryDefinition:
    slices = [NONE_OPT]
    products = Product.objects.all().order_by("-validity_to")
    slice_codes = []
    for product in products:
        cleaned_code = clean_code(str(product.code))
        if cleaned_code not in slice_codes:
            slice_codes.append(cleaned_code)
            slices.append(
                ADXCategoryOptionDefinition(
                    code=cleaned_code,
                    name=(
                        f"{product.code}-{product.name}"
                        if not product.name.startswith(product.code)
                        else product.name
                    ),
                    # filter=Q(**{f'{prefix}product':product})
                )
            )

    return ADXMappingCategoryDefinition(
        category_name="product", category_options=slices, path=f"{prefix}code"
    )
