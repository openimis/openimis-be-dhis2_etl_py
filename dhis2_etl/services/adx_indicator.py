import datetime
from xml.etree import ElementTree

from location.models import HealthFacility, Location

from dhis2_etl.adx_transform.formatters import XMLFormatter
from dhis2_etl.adx_transform.builders import ADXBuilder
from dhis2_etl.utils import api
from .adx.cubes import get_enrollment_cube, get_claim_cube

from .adx.utils import get_last_day_of_last_month

from ..models.dhis2Enum import MergeMode


def post_enrollment_cube(period):
    # Nombre d’adhérents par district, par municipalité, par sexe, par âge
    org_units = list(Location.objects.all().filter(validity_to__isnull=True).filter(type='M'))
    builder = ADXBuilder(get_enrollment_cube(period))
    insuree_data = builder.create_adx_cube(period, org_units)
    insuree_data = ElementTree.tostring(XMLFormatter().format_adx(insuree_data))
    return api.post(
        'dataValueSets',
        data={'data': insuree_data},
        file_type='xml',
        params={'mergeMode': MergeMode.merge, 'Content-Type': 'application/adx+xml'})


def post_claim_cube(period):
    # Nombre dde claim/benefices
    org_units = list(HealthFacility.objects.all().filter(validity_to__isnull=True))
    builder = ADXBuilder(get_claim_cube(period))
    insuree_data = builder.create_adx_cube(period, org_units)
    insuree_data = ElementTree.tostring(XMLFormatter().format_adx(insuree_data))
    return api.post(
        'dataValueSets',
        data={'data': insuree_data},
        file_type='xml',
        params={'mergeMode': MergeMode.merge, 'Content-Type': 'application/adx+xml'})


def sync():
    # number of insuree
    refDate = get_last_day_of_last_month(datetime.datetime.now())
    period = refDate.strftime("%YW%m")
    period = "2015-01-01/P9Y"
    post_enrollment_cube(period)
    post_claim_cube(period)
