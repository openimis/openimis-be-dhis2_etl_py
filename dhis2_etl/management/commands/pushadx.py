# import the logging library


# Create your views here.

from django.core.management.base import BaseCommand

from dhis2_etl.management.utiils import set_logger
from dhis2_etl.scheduled_tasks import adx_monthly_sync
from dhis2_etl.services.adx_metadata import build_categories
from dhis2_etl.models.dhis2.metadata import MetadataBundle
import datetime
from dhis2_etl.services.adx.cubes import get_claim_cube, get_enrollment_cube
from dhis2_etl.services.adx.utils import get_first_day_of_last_month
from dhis2_etl.strategy.dhis2_client import postRaw
from dhis2_etl.strategy.adx_client import ADXClient

logger = set_logger(False)
    


class Command(BaseCommand):
    help = "This command will generate the metadate and data update for dhis2 and push it."

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            help='Be verbose about what it is doing',
        )
        parser.add_argument("date", nargs=1, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'))
        parser.add_argument("scope", nargs=1, choices=[
            'pushLastMonth',
            'pushMetadata'
        ])
        
    def handle(self, *args, **options):
        
        verbose = options["verbose"]
        #if verbose:
        #    logger = set_logger(True)
        date = options["date"][0]
        scope = options["scope"][0]
        if scope is None:
            scope = "pushLastMonth"
        logger.info("Start sync ADX %s ", scope )
        self.sync_adx(date, scope)
        logger.info("sync ADX done")

    def sync_adx(self,date, scope):
        if scope == 'pushLastMonth':
            adx_monthly_sync(date)
        if scope == 'pushMetadata':
            period_start = get_first_day_of_last_month(date)
            period_start = period_start.strftime("%Y-%m-%d")
            period = f'{period_start}/P1M'
            categoryOptions, categories , categoryCombo , dataElement , dataSets = build_categories(get_enrollment_cube(period))
            
            
            categoryOptions, categories , categoryCombo , dataElement , dataSets = build_categories(get_claim_cube(period),categoryOptions, categories , categoryCombo , dataElement, dataSets)
            bundle = MetadataBundle(
                categoryOptions = categoryOptions,
                categories = list(categories.values()),
                categoryCombos = list(categoryCombo.values()),
                dataElements = dataElement,
                dataSets = dataSets
            )
            postRaw('metadata',bundle)
            with ADXClient() as adx_client:
                adx_client.updateOrgUnitAndCatComboOption()


             
