
# Service to push openIMIS location and HF to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
from ..models.dhis2Metadata import *
#import time
from django.http import  JsonResponse
from ..converters.LocationConverter import LocationConverter
from location.models import Location, HealthFacility
#from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Prefetch, F
# FIXME manage permissions
from ..utils import *

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated   


def syncRegion(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='R')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj, group_name='Region', id = 'UMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj, group_name='Region', id = 'UMRPiQP7N4v' , page_size = 1000 )) 
    return res

def syncDistrict(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='D')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='District', id = 'TMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='District', id = 'TMRPiQP7N4v'  , page_size = 1000)) 
    return res

def syncWard(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='W')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Ward', id = 'TMRPiQP8N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Ward', id = 'TMRPiQP8N4v' , page_size = 1000)) 
    return res

def syncVillage(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='V')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Village' , id = 'TMRPiQT7N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Village' , id = 'TMRPiQT7N4v' , page_size = 1000)) 
    return res

def syncHospital(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(legacy_id__isnull=True)  |Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='H')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Hospitals', id = 'WMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Hospitals', id = 'WMRPiQP7N4v'  , page_size = 1000)) 
    return res
def syncDispensary(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(legacy_id__isnull=True)  |Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='D')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj, group_name='Dispensary' , id = 'XMRPiQP7N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj, group_name='Dispensary' , id = 'XMRPiQP7N4v' , page_size = 1000)) 
    return res
    
def syncHealthCenter(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(legacy_id__isnull=True) |Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='C')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs , page_size = 1000)   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='HealthCenter', id = 'YMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='HealthCenter', id = 'YMRPiQP7N4v' , page_size = 1000 )) 
    return res