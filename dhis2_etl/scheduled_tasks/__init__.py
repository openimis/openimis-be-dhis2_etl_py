import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.scheduled_tasks.sync_function import DailySync, SyncFunction
from dhis2_etl.scheduled_tasks.utils import (sync_location_if_changed,
                                             sync_optionset_if_changed,
                                             sync_product_if_changed)
from dhis2_etl.services.adx_service import ADXService
from dhis2_etl.services.claimServices import syncClaim
from dhis2_etl.services.fundingServices import sync_funding
from dhis2_etl.services.insureeServices import syncPolicy
from dhis2_etl.strategy.adx_client import ADXClient

logger = logging.getLogger('openIMIS')

SYNC_FUNCTIONS = [
    SyncFunction("claim", syncClaim, GeneralConfiguration.get_scheduled_integration('claims')),
    SyncFunction("policies", syncPolicy, GeneralConfiguration.get_scheduled_integration('policies')),
    SyncFunction("contribution", sync_funding, GeneralConfiguration.get_scheduled_integration('contribution')),
    SyncFunction("product", sync_product_if_changed, GeneralConfiguration.get_scheduled_integration('product')),
    SyncFunction("other_optionset", sync_optionset_if_changed,
                 GeneralConfiguration.get_scheduled_integration('other_optionset')),
    SyncFunction("location", sync_location_if_changed, GeneralConfiguration.get_scheduled_integration('location')),
]


def schedule_daily_sync():
    daily_sync = DailySync(SYNC_FUNCTIONS)
    daily_sync.sync()


def adx_monthly_sync(date):
    with ADXClient() as adx_client:
        service = ADXService.last_month(date)
        service.build_enrolment_cube(adx_client.post_cube)
        service.build_claim_cube(adx_client.post_cube)



def schedule_tasks(scheduler: BackgroundScheduler):
    # scheduler.add_job(
    #     schedule_daily_sync,
    #     trigger=CronTrigger(hour=8),  # Daily at 8 AM
    #     id="dhis2_data_sync",  # The `id` assigned to each job MUST be unique
    #     max_instances=1,
    #     replace_existing=True,
    # )

    scheduler.add_job(
        adx_monthly_sync,
        trigger=CronTrigger(day=1, hour=4),  # Monthly on 1st at 4 AM
        id="dhis2_adx_monthly_sync",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )
