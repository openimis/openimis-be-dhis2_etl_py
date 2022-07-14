import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.scheduled_tasks.sync_function import SyncFunction, DailySync
from dhis2_etl.scheduled_tasks.utils import sync_product_if_changed, sync_optionset_if_changed, sync_location_if_changed
from dhis2_etl.services.claimServices import syncClaim
from dhis2_etl.services.fundingServices import sync_funding
from dhis2_etl.services.insureeServices import syncPolicy

SYNC_FUNCTIONS = [
    SyncFunction("claim", syncClaim, GeneralConfiguration.get_scheduled_integration('claims')),
    SyncFunction("policies", syncPolicy, GeneralConfiguration.get_scheduled_integration('policies')),
    SyncFunction("contribution", sync_funding, GeneralConfiguration.get_scheduled_integration('contribution')),
    SyncFunction("product", sync_product_if_changed, GeneralConfiguration.get_scheduled_integration('product')),
    SyncFunction("other_optionset", sync_optionset_if_changed, GeneralConfiguration.get_scheduled_integration('other_optionset')),
    SyncFunction("location", sync_location_if_changed, GeneralConfiguration.get_scheduled_integration('location')),
]


def schedule_daily_sync():
    daily_sync = DailySync(SYNC_FUNCTIONS)
    daily_sync.sync()


def schedule_tasks(scheduler: BackgroundScheduler):
    scheduler.add_job(
        schedule_daily_sync,
        trigger=CronTrigger(hour=8),  # Daily at 8 AM
        id="dhis2_data_sync",  # The `id` assigned to each job MUST be unique
        max_instances=1,
        replace_existing=True,
    )
