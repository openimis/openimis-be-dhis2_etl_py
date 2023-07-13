# Service to push openIMIS claim to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
# import the logging library
import logging

from claim.models import Claim, ClaimItem, ClaimService
from django.db.models import Prefetch, Q
#import time
from django.http import JsonResponse

#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder

from dhis2_etl.builders.dhis2.ClaimConverter import (CLAIM_REJECTED,
                                                     CLAIM_VALUATED,
                                                     ClaimConverter)
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.strategy.dhis2_client import *
# FIXME manage permissions
from dhis2_etl.utils import *

# Get an instance of a logger
logger = logging.getLogger('openIMIS')

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated

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
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True)))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True)))\
            .order_by('validity_from')
    # get the insuree matching the search
    return postMethod('enrollments',claims, ClaimConverter.to_enrollment_objs, event = True)

   
def syncClaimEvent(startDate,stopDate):
    # get only the last version of valudated or rejected claims (to sending multiple time the same claim)
    claims = Claim.objects.filter(validity_to__isnull=True)\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(Q(status=CLAIM_VALUATED) | Q(status=CLAIM_REJECTED))\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('admin')\
            .select_related('health_facility')\
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True).select_related('item')))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True).select_related('service')))\
            .order_by('validity_from')
    # get the insuree matching the search
    return postMethod('events', claims, ClaimConverter.to_event_objs, event=True)
