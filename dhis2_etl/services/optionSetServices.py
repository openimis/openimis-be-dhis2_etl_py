# Service to push list as optionSet in DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>


# import the logging library
import logging

from insuree.models import Education, FamilyType, Gender, Profession
from medical.models import Diagnosis, Item, Service
from product.models import Product

#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder

#import time
from dhis2_etl.builders.dhis2.OptionSetConverter import OptionSetConverter
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.strategy.dhis2_client import *
# FIXME manage permissions
from dhis2_etl.utils import *

# Get an instance of a logger
logger = logging.getLogger('openIMIS')

postMethod = post
# postMethod = postPaginated
# postMethod = postPaginatedThreaded
# postMethod = printPaginated   


def syncGender(startDate,stopDate):
    genders = Gender.objects.all()
    res = postMethod('metadata', genders, OptionSetConverter.to_option_objs, \
        optiontSetName = 'gender',\
        att1 = 'gender',\
        att2 = '',\
        code = 'code')
    res = postMethod('metadata', genders, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'gender',\
        code = 'code')
    return res

def syncProfession(startDate,stopDate):
    professions = Profession.objects.all()
    res = postMethod('metadata', professions, OptionSetConverter.to_option_objs, \
        optiontSetName = 'profession',\
        att1 = 'profession',\
        att2 = '',\
        code = 'id')
    res = postMethod('metadata', professions, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'profession',\
        code = 'id')
    return res


def syncGroupType(startDate,stopDate):
    groupTypes = FamilyType.objects.all()
    res = postMethod('metadata', groupTypes, OptionSetConverter.to_option_objs, \
        optiontSetName = 'groupType',\
        att1 = 'type',\
        att2 = '',\
        code = 'code')
    res = postMethod('metadata', groupTypes, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'groupType',\
        code = 'code')
    return res

def syncEducation(startDate,stopDate):
    educations = Education.objects.all()
    res = postMethod('metadata', educations, OptionSetConverter.to_option_objs, \
        optiontSetName = 'education',\
        att1 = 'education',\
        att2 = '',\
        code = 'id')
    res = postMethod('metadata', educations, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'education',\
        code = 'id')
    return res


def syncProduct(startDate,stopDate):
    products = Product.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)
    res = postMethod('metadata', products, OptionSetConverter.to_option_objs, \
        optiontSetName = 'product',\
        att1 = 'code',\
        att2 = 'name',\
        code = 'id')
    res = postMethod('metadata', products, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'product',\
        code = 'id')
    return res

def syncDiagnosis(startDate,stopDate):
    diagnosis = Diagnosis.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)
    res = postMethod('metadata', diagnosis, OptionSetConverter.to_option_objs, \
        optiontSetName = 'diagnosis',\
        att1 = 'code',\
        att2 = 'name',\
        code = 'id')
    res = postMethod('metadata', diagnosis, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'diagnosis',\
        code = 'id')
    return res

    
def syncItem(startDate,stopDate):
    items = Item.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)
    res = postMethod('metadata', items, OptionSetConverter.to_option_objs, \
        optiontSetName = 'item',\
        att1 = 'code',\
        att2 = 'name',\
        code = 'id')
    res = postMethod('metadata', items, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'item',\
        code = 'id')
    return res

    
def syncService(startDate,stopDate):
    services = Service.objects.filter(legacy_id__isnull=True)\
        .filter(validity_from__lte=stopDate)\
        .filter(validity_from__gte=startDate)
    res = postMethod('metadata', services, OptionSetConverter.to_option_objs, \
        optiontSetName = 'service',\
        att1 = 'code',\
        att2 = 'name',\
        code = 'id')
    res = postMethod('metadata', services, OptionSetConverter.to_optionsets_bundled, \
        optiontSetName = 'service',\
        code = 'id')
    return res