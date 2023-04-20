from typing import List

from dhis2_etl.adx_transform import ADXBuilder
from dhis2_etl.adx_transform.adx_models.adx_data import ADXMapping
from dhis2_etl.adx_transform.adx_models.adx_definition import ADXMappingCubeDefinition
from dhis2_etl.services.adx.cubes import get_claim_cube, get_enrollment_cube
from dhis2_etl.services.adx.utils import get_first_day_of_last_month
from location.models import HealthFacility, Location


class ADXService:
    @classmethod
    def last_month(cls):
        """
        Returns ADXService instance with period for last month i.e. if created on 2023-01-03 the period will be
        2022-12-01/P1M
        """
        period_start = get_first_day_of_last_month()
        period_start = period_start.strftime("%Y-%m-%d")
        return ADXService(f'{period_start}/P1M')

    def __init__(self, period: str):
        self.period = period

    def build_enrolment_cube(self) -> ADXMapping:
        org_units = list(Location.objects.all().filter(validity_to__isnull=True).filter(type='M'))
        return self._build_cube(get_enrollment_cube(self.period), org_units)

    def build_claim_cube(self) -> ADXMapping:
        org_units = list(HealthFacility.objects.all().filter(validity_to__isnull=True))
        return self._build_cube(get_claim_cube(self.period), org_units)

    def _build_cube(self, mapping_cube: ADXMappingCubeDefinition, org_units: List) -> ADXMapping:
        return ADXBuilder(mapping_cube).create_adx_cube(self.period, org_units)
