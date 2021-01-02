from django.shortcuts import render, redirect
from dhis2 import Api

#from django.http import HttpResponse, JsonResponse
import threading
from .models import *
#import time

from .converters import InsureeConverter, ClaimConverter
from insuree.models import Insuree, InsureePolicy
from claim.models import Claim
#from policy.models import Policy
 
from .configuration import GeneralConfiguration
from .model import ProgramBundle
import requests
from django.db.models import Q, prefetch
# FIXME manage permissions

# Get DHIS2 credentials from the config
dhis2 = GeneralConfiguration.get_dhis2()
# create the DHIS2 API object
api = Api(dhis2.host, dhis2.username, dhis2.password)
# define the page size
page_size = GeneralConfiguration.get_default_page_size()
# Create your views here.

def startThreadTask(request):
    task = ThreadTask()
    task.save()
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')
    scope = request.GET.get('scope')
    if scope is None:
        scope = "all"
    t = threading.Thread(target=SyncDHIS2,args=[task.id, starteDate, stopeDate, scope])
    t.setDaemon(True)
    t.start()
    return JsonResponse({'id':task.id})

def checkThreadTask(request,id):
    task = ThreadTask.objects.get(pk=id)
    return JsonResponse({'is_done':task.is_done})

def SyncDHIS2(id, startDate, stopDate, scope):
    print("Received task",id)
    responses = []
    task = ThreadTask.objects.get(pk=id)
    if scope == "all" or scope == "insuree":
        responses.insert(syncInsuree(startDate,stopDate))
    if scope == "all" or scope == "policy":
        responses.insert(syncPolicy(startDate,stopDate))
    if scope == "all" or scope == "claim":
        responses.insert(syncClaim(startDate,stopDate))
    if scope == "all" or scope == "claimdetail":
        responses.insert(syncClaimDetail(startDate,stopDate))
    task.is_done = True
    task.save()
    print("Finishing task",id)

def syncInsuree(startDate,stopDate):
    # get the insuree matching the search
    insurees = Insuree.objects.filter(Q(validity_to__isnull=True) | Q(validity_to__lte=stopDate))\
            .filter(validity_from__gte=startDate)\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')
            
    trackedEntityInstances = InsureeConverter.to_tei_obj(insurees)
    # Send the Insuree page per page, page size defined by config get_default_page_size
    return api.post_partitioned('TrackedEntityInstance',\
        {"TrackedEntityInstances" : trackedEntityInstances.json()}, \
        {"mergeMode": "REPLACE"},\  
        page_size )
    

def syncPolicy(startDate,stopDate):
    # get params from the request
    policies = InsureePolicy.objects.filter(Q(validity_to__isnull=True) | Q(validity_to__lte=stopDate))\
            .filter(validity_from__gte=startDate)\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('policy')\
            .select_related('insuree__family__location__uuid')\
            .select_related('policy__product')
    # get the policy matching the search
    events = InsureeConverter.to_event_obj(policies)
    # Send the Insuree page per page, page size defined by config get_default_page_size
    return api.post_partitioned('Event',\
            {"Events" : events.json()}, \
        {"mergeMode": "REPLACE"},\
        page_size )

    
def syncClaim(starteDate,stopDate):
    # get only the last version of valudated or rejected claims (to sending multiple time the same claim)
    claims = Claim.objects.filter(validity_to__isnull=True)
            .filter(validity_from__gte=startDate)
            .filter(validity_from__gte=startDate)
            .filter(Q(status=CLAIM_VALUATED)| Q(status=CLAIM_REJECTED))
            .order_by('validity_from')\
            .select_related('insuree__uuid')\
            .select_related('admin__uuid')\
            .select_related('health_facility__uuid')\
            .select_related('icd')\
            .select_related('icd_1')\
            .select_related('icd_2')\
            .select_related('icd_3')\
            .select_related('icd_4')\
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True).select_related('item')))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True).select_related('service')))\
            .order_by('validity_from')
    # get the insuree matching the search
    trackedEntityInstances = ClaimConverter.to_tei_obj(claims)
    # Send the Insuree page per page, page size defined by config get_default_page_size
    return api.post_partitioned('TrackedEntityInstance',\
        {"TrackedEntityInstances" : trackedEntityInstances.json()}, \
        {"mergeMode": "REPLACE"},\
        page_size )

  def syncClaimDetail(starteDate,stopDate):
    # get the list of todos
            
    events = ClaimConverter.to_event_obj(claims)
    return api.post_partitioned('Event',\
        {"Events" : events.json()}, \
        {"mergeMode": "REPLACE"},\
        page_size )
