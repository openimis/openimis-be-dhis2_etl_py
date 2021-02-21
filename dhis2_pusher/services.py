import threading
from .models.dhis2 import *
from .models.threading import *
#import time
from django.http import  JsonResponse
from .converters.LocationConverter import LocationConverter
from .converters.InsureeConverter import InsureeConverter
from .converters.ClaimConverter import ClaimConverter, CLAIM_VALUATED, CLAIM_REJECTED
from insuree.models import Insuree, InsureePolicy
from claim.models import Claim, ClaimItem, ClaimService
from location.models import Location, HealthFacility
#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder
from .configurations import GeneralConfiguration

from django.db.models import Q, Prefetch
# FIXME manage permissions
from .utils import *

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

postMethod = postPaginatedThreaded
def syncInsuree(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(legacy_id__isnull=True)\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
            .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')
    return postMethod('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs)

def syncInsureePolicy(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(legacy_id__isnull=True)\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
                .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')\
            .prefetch_related(Prefetch('insuree_policies', queryset=InsureePolicy.objects.filter(validity_to__isnull=True)\
                    .filter(expiry_date__isnull=False)\
                    .select_related('policy')\
                    .select_related('policy__product').only('policy__stage','policy__status','policy__value','policy__product__code',\
                'policy__product__name','policy__expiry_date', 'enrollment_date','id','insuree_id')))
            
    return postMethod('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs, event = True)




# fetch the policy in the database and send them to DHIS2
def syncPolicy(startDate,stopDate):
    # get params from the request
    # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    policies = InsureePolicy.objects.filter(validity_to__isnull=True)\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(expiry_date__isnull=False)\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('policy')\
            .select_related('insuree__family__location')\
            .select_related('policy__product')\
            .only('insuree__family__location__uuid','policy__stage','policy__status','policy__value','policy__product__code','insuree__uuid',\
                'policy__product__name','policy__expiry_date', 'enrollment_date')
    return postMethod('events',policies, InsureeConverter.to_event_objs)
    
def syncClaim(startDate,stopDate):
    # get only the last version of valudated or rejected claims (to sending multiple time the same claim)
    claims = Claim.objects.filter(validity_to__isnull=True)\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(Q(status=CLAIM_VALUATED)| Q(status=CLAIM_REJECTED))\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('admin')\
            .select_related('health_facility')\
            .select_related('icd')\
            .select_related('icd_1')\
            .select_related('icd_2')\
            .select_related('icd_3')\
            .select_related('icd_4')\
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True).select_related('item')))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True).select_related('service')))\
            .order_by('validity_from')
    # get the insuree matching the search
    return postMethod('trackedEntityInstances',claims, ClaimConverter.to_enrolment_objs)

def syncRegion(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='R')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(post('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj, group_name='Region', id = 'UMRPiQP7N4v' )) 
    return res

def syncDistrict(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='D')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(post('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj,  group_name='District', id = 'TMRPiQP7N4v' )) 
    return res

def syncWard(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='W')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(postPaginated('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj,  group_name='Ward', id = 'TMRPiQP8N4v')) 
    return res

def syncVillage(startDate,stopDate):
    locations = Location.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(type='V')\
        .select_related('parent')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(postPaginated('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj,  group_name='Village' , id = 'TMRPiQT7N4v')) 
    return res

def syncHospital(startDate,stopDate):
    locations = HealthFacility.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='H')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(post('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj,  group_name='Hospitals', id = 'WMRPiQP7N4v' )) 
    return res
def syncDispensary(startDate,stopDate):
    locations = HealthFacility.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='D')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(postPaginated('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj, group_name='Dispensary' , id = 'XMRPiQP7N4v')) 
    return res
    
def syncHealthCenter(startDate,stopDate):
    locations = HealthFacility.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)\
        .filter(level='D')\
        .select_related('location')
    res=postMethod('metadata',locations, LocationConverter.to_org_unit_objs)   
    res.append(postPaginated('organisationUnitGroups',locations, LocationConverter.to_org_unit_group_obj,  group_name='HealthCenter', id = 'YMRPiQP7N4v' )) 
    return res