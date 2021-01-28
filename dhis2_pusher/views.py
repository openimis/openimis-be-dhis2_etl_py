from django.shortcuts import render, redirect



import threading
from .models.dhis2 import *
from .models.threading import *
#import time
from django.http import  JsonResponse
from .converters.InsureeConverter import InsureeConverter
from .converters.ClaimConverter import ClaimConverter, CLAIM_VALUATED, CLAIM_REJECTED
from insuree.models import Insuree, InsureePolicy
from claim.models import Claim, ClaimItem, ClaimService
#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder
from .configurations import GeneralConfiguration

from django.db.models import Q, Prefetch
# FIXME manage permissions
from .utils import postPaginated

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.

def startThreadTask(request):
    #task = ThreadTask()
    #task.save()
    id = 1
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')
    scope = request.GET.get('scope')
    if scope is None:
        scope = "all"
    if startDate != None and stopDate != None:
        #t = threading.Thread(target=SyncDHIS2,args=(task.id, startDate, stopDate, scope))
        #t.setDaemon(True)
        #t.start()
        logger.debug("Start SyncDHIS2")
        SyncDHIS2(id, startDate, stopDate, scope)
        return JsonResponse({'id':id})
    else:
        return "Please specify startDate and stopDate using yyyy-mm-dd format"

def checkThreadTask(request,id):
    task = ThreadTask.objects.get(pk=id)
    return JsonResponse({'is_done':task.is_done})

def SyncDHIS2(id, startDate, stopDate, scope):
    logger.debug("Received task",id)
    responses = []
    ##task = ThreadTask.objects.get(pk=id)
    if scope == "all" or scope == "insuree":
        logger.debug("start Insuree sync")
        insureeResponse = syncInsuree(startDate,stopDate)
        logger.debug(insureeResponse)

        #responses.insert(insureeResponse)
    if scope == "all" or scope == "policy":
        logger.debug("start Policy sync")
        policyResponse = syncPolicy(startDate,stopDate)
        logger.debug(policyResponse)

        #responses.insert(policyResponse)
    if scope == "all" or scope == "claim":
        logger.debug("start Claim sync")
        claimResponse = syncClaim(startDate,stopDate)
        logger.debug(claimResponse)


        #responses.insert(claimResponse)
    #if scope == "all" or scope == "claimdetail":
    #    responses.insert(syncClaimDetail(startDate,stopDate))
    #task.is_done = True
    ##task.save()
    logger.debug("Finishing task",id)

def syncInsuree(startDate,stopDate):
    # get the insuree matching the search
    insurees = Insuree.objects.filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
            .only('profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from')
    return postPaginated('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs)




# fetch the policy in the database and send them to DHIS2
def syncPolicy(startDate,stopDate):
    # get params from the request
    # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    policies = InsureePolicy.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('policy')\
            .select_related('insuree__family__location')\
            .select_related('policy__product')\
            .only('insuree__family__location__uuid','policy__stage','policy__status','policy__value','insuree__uuid',\
                'policy__product__code','policy__product__name','policy__expiry_date', 'enrollment_date')
    return postPaginated('events',policies, InsureeConverter.to_event_objs)
    
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
    return postPaginated('trackedEntityInstances',claims, ClaimConverter.to_tei_objs)


