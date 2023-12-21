
# Service to push openIMIS location and HF to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
# import the logging library
import logging

#import time
from dhis2_etl.builders.dhis2.LocationConverter import LocationConverter
from dhis2_etl.models.dhis2.metadata import *
#from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Q
from location.models import HealthFacility, Location

# FIXME manage permissions
from dhis2_etl.utils import *
from dhis2_etl.strategy.dhis2_client import *


# Get an instance of a logger
logger = logging.getLogger('openIMIS')

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated   

def createRootOrgUnit():
    res=postRaw('metadata',LocationConverter.getRootOrgUnit())
    return res



def syncRegion(startDate,stopDate):
    locations = Location.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='R')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj, group_name='Region', id = 'UMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj, group_name='Region', id = 'UMRPiQP7N4v'  )) 
    return res

def syncDistrict(startDate,stopDate):
    locations = Location.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='D')\
        .filter(parent__type='R')\
        .filter(Q(parent__validity_to__isnull=True) | Q(parent__legacy_id=F('id')))\
        .select_related('parent')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='District', id = 'TMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='District', id = 'TMRPiQP7N4v'  )) 
    return res

def syncWard(startDate,stopDate):
    locations = Location.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='W')\
        .filter(parent__type='D')\
        .filter(Q(parent__validity_to__isnull=True) | Q(parent__legacy_id=F('id')))\
        .filter(parent__parent__type='R')\
        .filter(Q(parent__parent__validity_to__isnull=True) | Q(parent__parent__legacy_id=F('id')))\
        .select_related('parent')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Ward', id = 'TMRPiQP8N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Ward', id = 'TMRPiQP8N4v' )) 
    return res

def syncVillage(startDate,stopDate):
    locations = Location.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='V')\
        .filter(parent__type='W')\
        .filter(Q(parent__validity_to__isnull=True) | Q(parent__legacy_id=F('id')))\
        .filter(parent__type='D')\
        .filter(Q(parent__parent__validity_to__isnull=True) | Q(parent__parent__legacy_id=F('id')))\
        .filter(parent__parent__type='R')\
        .filter(Q(parent__parent__parent__validity_to__isnull=True) | Q(parent__parent__parent__legacy_id=F('id')))\
        .select_related('parent')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Village' , id = 'TMRPiQT7N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Village' , id = 'TMRPiQT7N4v' )) 
    return res

def syncHospital(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='H')\
        .filter(location__type='D')\
        .filter(Q(location__validity_to__isnull=True) | Q(location__legacy_id=F('id')))\
        .filter(location__parent__type='R')\
        .filter(Q(location__parent__validity_to__isnull=True) | Q(location__parent__legacy_id=F('id')))\
        .select_related('location')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj,  group_name='Hospitals', id = 'WMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='Hospitals', id = 'WMRPiQP7N4v'  )) 
    return res

def syncDispensary(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='D')\
        .filter(location__type='D')\
        .filter(Q(location__validity_to__isnull=True) | Q(location__legacy_id=F('id')))\
        .filter(location__parent__type='R')\
        .filter(Q(location__parent__validity_to__isnull=True) | Q(location__parent__legacy_id=F('id')))\
        .select_related('location')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj, group_name='Dispensary' , id = 'XMRPiQP7N4v')) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj, group_name='Dispensary' , id = 'XMRPiQP7N4v' )) 
    return res
    
def syncHealthCenter(startDate,stopDate):
    locations = HealthFacility.objects.filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='C')\
        .filter(location__type='D')\
        .filter(Q(location__validity_to__isnull=True) | Q(location__legacy_id=F('id')))\
        .filter(location__parent__type='R')\
        .filter(Q(location__parent__validity_to__isnull=True) | Q(location__parent__legacy_id=F('id')))\
        .select_related('location')\
        .order_by('validity_from')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs )   
    res.append(post('metadata',None, LocationConverter.to_org_unit_group_obj, group_name='HealthCenter', id = 'YMRPiQP7N4v' )) 
    res.append(postPaginated('metadata',locations, LocationConverter.to_org_unit_group_obj,  group_name='HealthCenter', id = 'YMRPiQP7N4v'  )) 
    return res

def syncPopulation(atDate):
    # from < date and to null or to < data
    # issue old data don't get uuid 
    atYear = atDate[ 0: 4]
    locations = Location.objects\
        .filter(validity_from__lte=atDate)\
        .filter(Q(validity_to__gte=atDate)|Q(validity_to__isnull=True))\
        .filter(type='V')\
        .filter(parent__type='W')\
        .filter(Q(parent__validity_to__isnull=True) | Q(parent__legacy_id=F('id')))\
        .filter(parent__type='D')\
        .filter(Q(parent__parent__validity_to__isnull=True) | Q(parent__parent__legacy_id=F('id')))\
        .filter(parent__parent__type='R')\
        .filter(Q(parent__parent__parent__validity_to__isnull=True) | Q(parent__parent__parent__legacy_id=F('id')))\
        .filter(Q(male_population__gt=0)|Q(female_population__gt=0)|Q(other_population__gt=0)|Q(families__gt=0))\
        .order_by('validity_from')
        # .select_related
    res=postMethod('dataValueSets',locations, LocationConverter.to_population_datavaluesets, data_set_period = atYear, page_size = 1000)   
    #if locations is not None:
    #    for location in locations:
    #        res=post('dataValueSets',location, LocationConverter.to_population_dataset, data_set_period = atYear)
    #return res