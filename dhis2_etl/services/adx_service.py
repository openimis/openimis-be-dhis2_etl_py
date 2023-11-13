import logging
from typing import List
from django.db.models import Q, F
from dhis2_etl.builders.adx import ADXBuilder
from dhis2_etl.models.adx.data import ADXMapping
from dhis2_etl.models.adx.definition import ADXMappingCubeDefinition
from dhis2_etl.services.adx.cubes import get_claim_cube, get_enrollment_cube
from dhis2_etl.services.adx.utils import get_first_day_of_last_month
from location.models import HealthFacility, Location


logger = logging.getLogger('openIMIS')

class ADXService:
    PAGE_SIZE = 10
    
    def get_cube_builder(self):
        return [
            *self.build_enrolment_cube,
            *self.build_claim_cube
        ]
    
    @classmethod
    def last_month(cls,date = None):
        """
        Returns ADXService instance with period for last month i.e. if created on 2023-01-03 the period will be
        2022-12-01/P1M
        """
        period_start = get_first_day_of_last_month(date)
        period_start = period_start.strftime("%Y-%m-%d")
        return ADXService(f'{period_start}/P1M')

    def __init__(self, period: str):
        self.period = period

    def build_enrolment_cube(self, callback):
        org_units = list(Location.objects.all().filter(validity_to__isnull=True).filter(type='W').filter(parent__type='D')\
        .filter(Q(parent__validity_to__isnull=True) | Q(parent__legacy_id=F('id')))\
        .filter(parent__parent__type='R')\
        .filter(Q(parent__parent__validity_to__isnull=True) | Q(parent__parent__legacy_id=F('id'))))
        logger.debug('create enrolment cube for %i location', len(org_units))
        return self._build_cube(get_enrollment_cube(self.period), org_units, callback)

    def build_claim_cube(self, callback):
        org_units = list(HealthFacility.objects.all().filter(validity_to__isnull=True).filter(location__type='D')\
        .filter(Q(location__validity_to__isnull=True) | Q(location__legacy_id=F('id')))\
        .filter(location__parent__type='R')\
        .filter(Q(location__parent__validity_to__isnull=True) | Q(location__parent__legacy_id=F('id'))))
        logger.debug('create claim cube for %i location', len(org_units))
        return self._build_cube(get_claim_cube(self.period), org_units, callback)

    def _build_cube(self, mapping_cube: ADXMappingCubeDefinition, org_units: List, callback):
        for i in range(0, len(org_units), self.PAGE_SIZE):
            callback(ADXBuilder(mapping_cube).create_adx_cube(self.period, org_units[i:i+self.PAGE_SIZE]))
        
        

