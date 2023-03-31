from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingGroupDefinition
from dhis2_etl.services.adx.data_values import get_location_insuree_number_dv, get_location_family_number_dv, \
    get_location_contribution_sum_dv, get_hf_claim_number_dv, get_hf_claim_benefits_valuated_dv, \
    get_hf_claim_benefits_asked_dv, get_hf_benefit_number
from dhis2_etl.utils import build_dhis2_id
from location.models import Location, HealthFacility


def get_enrolment_location_group(period):
    return ADXMappingGroupDefinition(
        comment="number of insuree per location",
        dataset=Location,
        to_org_unit_code_func=lambda l: build_dhis2_id(l.uuid),
        data_values=[
            get_location_insuree_number_dv(period),
            get_location_family_number_dv(period),
            get_location_contribution_sum_dv(period)
        ]
    )


def get_claim_hf_group(period):
    return ADXMappingGroupDefinition(
        comment="number of claim per HF",
        dataset=HealthFacility,
        to_org_unit_code_func=lambda hf: build_dhis2_id(hf.uuid),
        data_values=[
            get_hf_claim_number_dv(period),
            get_hf_benefit_number(period),
            get_hf_claim_benefits_valuated_dv(period),
            get_hf_claim_benefits_asked_dv(period),
        ]
    )
