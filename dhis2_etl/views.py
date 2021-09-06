from django.shortcuts import render, redirect
from .services.claimServices import *
from .services.fundingServices import *
from .services.insureeServices import *
from .services.locationServices import *
from .services.optionSetServices import *
# import the logging library
import logging
import re
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.

def start_task(request):
    startDate = request.GET.get('startDate')
    stopDate = request.GET.get('stopDate')
    scope = request.GET.get('scope')
    regex = re.compile("^\d{4}-\d{2}-\d{2}$")
    if scope is None:
        scope = "all"
    if regex.match(startDate) and regex.match(startDate) :
        logger.debug("Start sync Dhis2")
        sync_dhis2(startDate, stopDate, scope)
        return JsonResponse({'Status':"Done"})
    else:
        return "Please specify startDate and stopDate using yyyy-mm-dd format"


def sync_dhis2(startDate, stopDate, scope):
    logger.debug("Received task")
    responses = []
    ## TEI and Program enrollment and event
    #########################################
    ## TODO policy only for renewalm insureePolicy for new
    if scope == "all" or scope == "insuree":
        logger.debug("start Insuree sync")
        insureeResponse = syncInsuree(startDate,stopDate)
    if scope == "all" or scope == "policy":
        logger.debug("start Policy sync")
        policyResponse = syncPolicy(startDate,stopDate)
    if scope == "all" or scope == "claim":
        logger.debug("start Claim sync")
        claimResponse = syncClaim(startDate,stopDate)
    # OTHER program sync
    ####################
    # manual enrollment to policy program
    if scope == 'enroll':
        logger.debug("start Insuree enroll")
        insureeResponse = enrollInsuree(startDate,stopDate)
        #responses.insert(insureeResponse)
    # syncInsuree and Policiy event
    if  scope == "insureepolicies":
        logger.debug("start Insuree & policy sync")
        insureePolicyResponse = syncInsureePolicy(startDate,stopDate)

    if  scope == "insureepoliciesclaims":
        logger.debug("start Insuree & policy & claim sync")
        insureePolicyclaimResponse = syncInsureePolicyClaim(startDate,stopDate)
    # ORGUNIT 
    #########
    if scope == 'createRoot':
        sync = createRootOrgUnit()

    if  scope == "orgunit":
        logger.debug("start orgUnit sync")
        syncRegionResponse = syncRegion(startDate,stopDate)
        syncDistrictResponse = syncDistrict(startDate,stopDate)
        syncWardResponse = syncWard(startDate,stopDate)
        syncVillageResponse = syncVillage(startDate,stopDate)
        syncHospitalResponse = syncHospital(startDate,stopDate)
        syncDispensaryResponse = syncDispensary(startDate,stopDate)
        syncHealthCenterResponse = syncHealthCenter(startDate,stopDate)

    # Optionset
    ###########
    if  scope == "optionset" :
            logger.debug("start OptionSets sync")
    if  scope == "optionset" or scope == "product":
        syncProductResponse = syncProduct(startDate,stopDate)
    if  scope == "optionset" or scope == "gender":
        syncGenderResponse = syncGender(startDate,stopDate)
    if  scope == "optionset" or scope == "profession":
        syncProfessionResponse = syncProfession(startDate,stopDate)
    if  scope == "optionset" or scope == "eduction":
        syncEducationResponse = syncEducation(startDate,stopDate)
    if  scope == "optionset" or scope == "grouptype":
        syncGroupTypeResponse = syncGroupType(startDate,stopDate)
    if  scope == "optionset" or scope == "diagnosis":
        syncDiagnosisResponse = syncDiagnosis(startDate,stopDate)
    if  scope == "optionset" or scope == "item":
        syncItemResponse =  syncItem(startDate,stopDate)
    if  scope == "optionset" or scope == "service":
        syncServiceResponse =  syncService(startDate,stopDate)


    # Dataset
    if  scope == "population":
        syncPopulationResponse =  syncPopulation(startDate)

    # funding
    if  scope == "funding":
        syncPopulationResponse =  sync_funding(startDate,stopDate)
    logger.debug("Finishing task")

