from dhis2_etl.models.adx.definition import ADXMappingGroupDefinition
from dhis2_etl.services.adx.data_values import get_location_insuree_number_dv, get_location_family_number_dv, \
    get_location_contribution_sum_dv, get_hf_claim_number_dv, get_hf_claim_benefits_valuated_dv, \
    get_hf_claim_benefits_asked_dv, get_hf_claim_item_number_dv, get_hf_claim_service_number_dv
from dhis2_etl.utils import build_dhis2_id, clean_code
from location.models import Location, HealthFacility


def get_enrolment_location_group(period):
    return ADXMappingGroupDefinition(
        comment="number of insuree per location",
        data_set='ENROLMENT',
        org_unit_type=Location,
        to_org_unit_code_func=lambda l:clean_code(l.uuid),
        data_values=[
            get_location_insuree_number_dv(period),
            get_location_family_number_dv(period),
            get_location_contribution_sum_dv(period)
        ]
    )
    



def get_claim_hf_group(period):
    return ADXMappingGroupDefinition(
        comment="number of claim per HF",
        data_set='PROCESSED_CLAIM',
        org_unit_type=HealthFacility,
        to_org_unit_code_func=lambda hf: clean_code(hf.uuid),
        data_values=[
            get_hf_claim_number_dv(period),
            get_hf_claim_item_number_dv(period),
            get_hf_claim_service_number_dv(period),
            get_hf_claim_benefits_valuated_dv(period),
            get_hf_claim_benefits_asked_dv(period),
        ]
    )
