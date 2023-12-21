# Service to push openIMIS insuree and policy to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
# import the logging library
import logging

from contribution.models import Premium

#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder

#import time
from dhis2_etl.builders.dhis2.FundingConverter import FundingConverter
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.strategy.dhis2_client import *
# FIXME manage permissions
from dhis2_etl.utils import *

# Get an instance of a logger
logger = logging.getLogger('openIMIS')

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated

def sync_funding(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    fundings = Premium.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(validity_to__isnull=True)\
            .filter(pay_type='F')\
            .order_by('validity_from')\
            .select_related('policy')\
            .filter(policy__validity_to__isnull=True)\
            .only('id','pay_date','policy__product_id','amount')
    return postMethod('events',fundings, FundingConverter.to_event_objs, page_size=200)
