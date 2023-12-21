# Service to push openIMIS insuree and policy to DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>
# import the logging library
import logging

from django.db.models import F, Prefetch, Q
#import time
from insuree.models import Insuree, InsureePolicy


from dhis2_etl.builders.dhis2.InsureeConverter import InsureeConverter
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.strategy.dhis2_client import *
# FIXME manage permissions
from dhis2_etl.utils import *

#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder



# Get an instance of a logger
logger = logging.getLogger('openIMIS')

postMethod = postPaginated
# postMethod = postPaginatedThreaded
#postMethod = printPaginated
def syncInsuree(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')))\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
            .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')
    return postMethod('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs, page_size=200)

def enrollInsuree(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(legacy_id__isnull=True)\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
            .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')
    return postMethod('enrollments',insurees, InsureeConverter.to_enrollment_objs, event = False,  page_size=200)

def syncInsureePolicy(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')) )\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
                .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')\
            .prefetch_related(Prefetch('insuree_policies', queryset=InsureePolicy.objects.filter(validity_to__isnull=True)\
                    .filter(expiry_date__isnull=False)\
                    .select_related('policy')\
                    .select_related('policy__product').only('policy__stage','policy__status','policy__value','policy__product__code',\
                'policy__product__name','expiry_date','start_date','effective_date', 'enrollment_date','id','insuree_id')))
            
    return postMethod('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs, event = True,  page_size=200)




# fetch the policy in the database and send them to DHIS2
def syncPolicy(startDate,stopDate):
    # get params from the request
    # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))\
    policies = InsureePolicy.objects.filter(validity_to__isnull=True)\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(expiry_date__isnull=False)\
            .order_by('validity_from')\
            .select_related('insuree')\
            .select_related('policy')\
            .select_related('insuree__family__location')\
            .only('policy__stage','insuree__family__location__uuid','policy__status','policy__value','policy__product_id',\
                'expiry_date','start_date','effective_date', 'enrollment_date','id','insuree_id','insuree__uuid')
    return postMethod('events',policies, InsureeConverter.to_event_objs, page_size=100)

def syncInsureePolicyClaim(startDate,stopDate):
    # get the insuree matching the search
        # get all insuree so we have also the detelted ones
    # .filter(Q(validity_to__isnull=True) | Q(validity_to__gte=stopDate))
    # TODO reverse link clainm
    from claim.models import Claim, ClaimItem, ClaimService

    from dhis2_etl.builders.ClaimConverter import (CLAIM_REJECTED,
                                                   CLAIM_VALUATED,
                                                   ClaimConverter)
    insurees = Insuree.objects\
            .filter(validity_from__lte=stopDate)\
            .filter(validity_from__gte=startDate)\
            .filter(Q(validity_to__isnull=True) | Q(legacy_id__isnull=True) | Q(legacy_id=F('id')) )\
            .order_by('validity_from')\
            .select_related('gender')\
            .select_related('family')\
            .select_related('family__location')\
            .select_related('health_facility')\
                .only('id','profession_id','family__poverty','chf_id','education_id','dob','family__uuid',\
                'family__family_type_id','other_names','gender_id','head','health_facility__uuid',\
                'marital','family__location__uuid','uuid','validity_from','last_name')\
            .prefetch_related(Prefetch('insuree_policies', queryset=InsureePolicy.objects.filter(validity_to__isnull=True)\
                .filter(validity_from__lte=stopDate)\
                .filter(validity_from__gte=startDate)\
                .filter(expiry_date__isnull=False)\
                    .select_related('policy')\
                    .only('policy__stage','policy__status','policy__value','policy__product_id',\
                'expiry_date','start_date','effective_date', 'enrollment_date','id','insuree_id')\
                    .order_by('validity_from')))\
            .prefetch_related(Prefetch('claim_set', Claim.objects.filter(validity_to__isnull=True)\
                .filter(validity_from__lte=stopDate)\
                .filter(validity_from__gte=startDate)\
                .filter(Q(status=CLAIM_VALUATED)| Q(status=CLAIM_REJECTED))\
                .order_by('validity_from')\
                .select_related('admin')\
                .select_related('health_facility')\
                .prefetch_related(Prefetch('items', queryset=ClaimItem.objects.filter(validity_to__isnull=True)))\
                .prefetch_related(Prefetch('services', queryset=ClaimService.objects.filter(validity_to__isnull=True)))\
                .order_by('validity_from')))
    return postMethod('trackedEntityInstances',insurees, InsureeConverter.to_tei_objs, event = True, claim = True)