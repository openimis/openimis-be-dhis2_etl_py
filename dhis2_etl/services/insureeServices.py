# Service to push openIMIS insuree and policy to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
from ..models.dhis2Program import *
#import time
from django.http import  JsonResponse
from ..converters.InsureeConverter import InsureeConverter
from insuree.models import Insuree, InsureePolicy
#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder

from django.db.models import Q, Prefetch
# FIXME manage permissions
from ..utils import *

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated
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

def enrollInsuree(startDate,stopDate):
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
    return postMethod('enrollments',insurees, InsureeConverter.to_enrollment_objs, event = False)

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
