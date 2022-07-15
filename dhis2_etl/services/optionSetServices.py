# Service to push list as optionSet in DHIS2
# Copyright Patrick Delcoix <patrick@pmpd.eu>


from ..models.dhis2Program import *
#import time
from django.http import  JsonResponse
from ..converters.OptionSetConverter import OptionSetConverter
from insuree.models import Gender, Profession, FamilyType, Education
from product.models import Product
from medical.models import Diagnosis, Item, Service
#from policy.models import Policy
#from django.core.serializers.json import DjangoJSONEncoder


from django.db.models import Q, Prefetch
# FIXME manage permissions
from ..utils import *

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

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