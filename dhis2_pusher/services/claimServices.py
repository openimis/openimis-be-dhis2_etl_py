# Service to push openIMIS claim to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
from ..models.dhis2Program import *
#import time
from django.http import  JsonResponse

from ..converters.ClaimConverter import ClaimConverter, CLAIM_VALUATED, CLAIM_REJECTED

from claim.models import Claim, ClaimItem, ClaimService

#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder


from django.db.models import Q, Prefetch
# FIXME manage permissions
from ..utils import *

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated   
def syncClaim(startDate,stopDate):
    # get only the last version of valudated or rejected claims (to sending multiple time the same claim)
    claims = Claim.objects.filter(validity_to__isnull=True)\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(insuree__legacy_id__isnull=True)\
            .filter(Q(status=CLAIM_VALUATED)| Q(status=CLAIM_REJECTED))\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('admin')\
            .select_related('health_facility')\
            .select_related('icd')\
            .select_related('icd_1')\
            .select_related('icd_2')\
            .select_related('icd_3')\
            .select_related('icd_4')\
            .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True).select_related('item')))\
            .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True).select_related('service')))\
            .order_by('validity_from')
    # get the insuree matching the search
    return postMethod('enrollments',claims, ClaimConverter.to_enrollment_objs, event = True)
