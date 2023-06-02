from django.core.management.base import BaseCommand
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

class Command(BaseCommand):
    help = "This command will generate the metadate and data update for dhis2 and push it."

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            help='Be verbose about what it is doing',
        )
        parser.add_argument("start_date", nargs=1, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
        parser.add_argument("stop_date", nargs=1, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
        parser.add_argument("scope", nargs=1, choices=[
            'all',
            'enroll',
            'insureepolicies',
            'insureepoliciesclaims',
            'createRoot', 
            'orgunit', 
            'optionset',
            'product',
            "gender",
            "profession",
            "education",
            "grouptype",
            "diagnosis",
            "item",
            "service",
            "population",
            "funding",
            "adx-categories",
            "adx-data"
            ] )


    def handle(self, *args, **options):
        verbose = options["verbose"]
        start_date = options["start_date"]
        stop_date = options["stop_date"]
        
        if scope is None:
            scope = "all"
        if regex.match(start_date) and regex.match(start_date) :
            logger.debug("Start sync Dhis2")
            self.sync_dhis2(start_date, stop_date, scope)
            logger.debug("sync Dhis2 done")
        else:
            logger.debug("Please specify start_date and stop_date using yyyy-mm-dd format")


    def sync_dhis2(start_date, stop_date, scope, verbose):
            logger.debug("Received task")
            responses = []
            ## TEI and Program enrollment and event
            #########################################
            ## TODO policy only for renewalm insureePolicy for new
            if scope == "all" or scope == "insuree":
                logger.debug("start Insuree sync")
                insureeResponse = syncInsuree(start_date,stop_date)
            if scope == "all" or scope == "policy":
                logger.debug("start Policy sync")
                policyResponse = syncPolicy(start_date,stop_date)
            if scope == "all" or scope == "claim":
                logger.debug("start Claim sync")
                claimResponse = syncClaim(start_date,stop_date)
            # OTHER program sync
            ####################
            # manual enrollment to policy program
            if scope == 'enroll':
                logger.debug("start Insuree enroll")
                insureeResponse = enrollInsuree(start_date,stop_date)
                #responses.insert(insureeResponse)
            # syncInsuree and Policiy event
            if  scope == "insureepolicies":
                logger.debug("start Insuree & policy sync")
                insureePolicyResponse = syncInsureePolicy(start_date,stop_date)

            if  scope == "insureepoliciesclaims":
                logger.debug("start Insuree & policy & claim sync")
                insureePolicyclaimResponse = syncInsureePolicyClaim(start_date,stop_date)
            # ORGUNIT 
            #########
            if scope == 'createRoot':
                sync = createRootOrgUnit()

            if  scope == "orgunit":
                logger.debug("start orgUnit sync")
                syncRegionResponse = syncRegion(start_date,stop_date)
                syncDistrictResponse = syncDistrict(start_date,stop_date)
                syncWardResponse = syncWard(start_date,stop_date)
                syncVillageResponse = syncVillage(start_date,stop_date)
                syncHospitalResponse = syncHospital(start_date,stop_date)
                syncDispensaryResponse = syncDispensary(start_date,stop_date)
                syncHealthCenterResponse = syncHealthCenter(start_date,stop_date)

            # Optionset
            ###########
            if  scope == "optionset" :
                    logger.debug("start OptionSets sync")
            if  scope == "optionset" or scope == "product":
                syncProductResponse = syncProduct(start_date,stop_date)
            if  scope == "optionset" or scope == "gender":
                syncGenderResponse = syncGender(start_date,stop_date)
            if  scope == "optionset" or scope == "profession":
                syncProfessionResponse = syncProfession(start_date,stop_date)
            if  scope == "optionset" or scope == "education":
                syncEducationResponse = syncEducation(start_date,stop_date)
            if  scope == "optionset" or scope == "grouptype":
                syncGroupTypeResponse = syncGroupType(start_date,stop_date)
            if  scope == "optionset" or scope == "diagnosis":
                syncDiagnosisResponse = syncDiagnosis(start_date,stop_date)
            if  scope == "optionset" or scope == "item":
                syncItemResponse =  syncItem(start_date,stop_date)
            if  scope == "optionset" or scope == "service":
                syncServiceResponse =  syncService(start_date,stop_date)


            # Dataset
            if  scope == "population":
                syncPopulationResponse =  syncPopulation(start_date)

            # funding
            if  scope == "funding":
                syncPopulationResponse =  sync_funding(start_date,stop_date)
            logger.debug("Finishing task")



