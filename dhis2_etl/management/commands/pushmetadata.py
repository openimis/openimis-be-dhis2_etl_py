# import the logging library
import re



# Create your views here.

from django.core.management.base import BaseCommand
from django.shortcuts import redirect, render
from dhis2_etl.management.utiils import set_logger
from dhis2_etl.scheduled_tasks import adx_monthly_sync

from dhis2_etl.services.claimServices import *
from dhis2_etl.services.fundingServices import *
from dhis2_etl.services.insureeServices import *
from dhis2_etl.services.locationServices import *
from dhis2_etl.services.optionSetServices import *
from dhis2_etl.strategy.adx_client import ADXClient
logger = set_logger()

    


class Command(BaseCommand):
    help = "This command will generate the metadate and data update for dhis2 and push it."

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            help='Be verbose about what it is doing',
        )
        parser.add_argument("reference_date", nargs=1, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
        parser.add_argument("scope", nargs=1, choices=[
            'all',
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
            ] )


    def handle(self, *args, **options):
        
        verbose = options["verbose"]
        reference_date = options["reference_date"][0]
        scope = options["scope"][0]
        if scope is None:
            scope = "all"
        #if verbose:
        #    logger = set_logger(True)
        logger.info("Start sync Dhis2 %s ", __package__ )
        self.sync_dhis2(reference_date, scope)
        logger.info("sync Dhis2 done")



    def sync_dhis2(self,  reference_date, scope):
        
            logger.info("Received task")
            responses = []
            stop_date = datetime.date.today()
            # ORGUNIT 
            #########
            if scope == 'createRoot' or scope == 'all':
                sync = createRootOrgUnit()

            if  scope == "orgunit" or scope == 'all':
                logger.info("start orgUnit sync")
                syncRegion(reference_date,stop_date)
                syncDistrict(reference_date,stop_date)
                syncWard(reference_date,stop_date)
                syncVillage(reference_date,stop_date)
                syncHospital(reference_date,stop_date)
                syncDispensary(reference_date,stop_date)
                syncHealthCenter(reference_date,stop_date)
                with ADXClient() as adx_client:
                    adx_client.updateOrgUnitAndCatComboOption()

            # Optionset
            ###########
            if  scope == "optionset" or scope == 'all' :
                    logger.info("start OptionSets sync")
            if  scope == "optionset" or scope == "product" or scope == 'all':
                syncProduct(reference_date,stop_date)
            if  scope == "optionset" or scope == "gender" or scope == 'all':
                syncGender(reference_date,stop_date)
            if  scope == "optionset" or scope == "profession" or scope == 'all':
                syncProfession(reference_date,stop_date)
            if  scope == "optionset" or scope == "education" or scope == 'all':
                syncEducation(reference_date,stop_date)
            if  scope == "optionset" or scope == "grouptype" or scope == 'all':
                syncGroupType(reference_date,stop_date)
            if  scope == "optionset" or scope == "diagnosis" or scope == 'all':
                syncDiagnosis(reference_date,stop_date)
            if  scope == "optionset" or scope == "item" or scope == 'all':
                syncItem(reference_date,stop_date)
            if  scope == "optionset" or scope == "service" or scope == 'all':
                syncService(reference_date,stop_date)


            # Dataset
            if  scope == "population":
                syncPopulation(reference_date)

            # funding
            if  scope == "funding":
                sync_funding(reference_date,stop_date)
            logger.info("Finishing task")

            if scope == 'adx-data':
                adx_monthly_sync()


