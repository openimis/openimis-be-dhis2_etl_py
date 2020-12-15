from django.shortcuts import render
from dhis2 import Api

from .serializers import InsureeSerializer, ClaimSerializer
from .configuration import GeneralConfiguration
from .model import ProgramBundle
import requests
#FIXME USE credential from config
dhis2 = GeneralConfiguration.get_dhis2()
api = Api(dhis2.host, dhis2.username, dhis2.password)
page_size = GeneralConfiguration.get_default_page_size()
# Create your views here.



def insuree(request):
    # get the list of todos
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')

    # get the insuree matching the search
    trackedEntityInstances = InsureeSerializer.getInsureeTrackedEntityInstances(startDate, stopDate)
    # Send the Insuree page per page, page size defined by config get_default_page_size
    api.post_partitioned('TrackedEntityInstance',
        {"TrackedEntityInstances" : trackedEntityInstances.json()}, 
        {"mergeMode": "REPLACE"},
        page_size )
    

def policy(request):
    # get the list of todos
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')

    events = InsureeSerializer.getPolicyEvents(startDate, stopDate)
    api.post_partitioned('Event',
            {"Events" : events.json()}, 
        {"mergeMode": "REPLACE"},
        page_size )

    
def claims(request):
    # get the list of todos
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')

    # get the insuree matching the search
    trackedEntityInstances = ClaimSerializer.getClaimTrackedEntityInstances(startDate, stopDate)
    # Send the Insuree page per page, page size defined by config get_default_page_size
    api.post_partitioned('TrackedEntityInstance',
        {"TrackedEntityInstances" : trackedEntityInstances.json()}, 
        {"mergeMode": "REPLACE"},
        page_size )

  def claimsDetails(request):
    # get the list of todos
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')
    events = ClaimSerializer.getClaimEvents(startDate, stopDate)
    api.post_partitioned('Event',
            {"Events" : events.json()}, 
        {"mergeMode": "REPLACE"},
        page_size )
