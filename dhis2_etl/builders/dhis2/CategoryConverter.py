# Copyrights Patrick Delcroix <patrick@pmpd.eu>
# Generic Converter to optionSet
# import the logging library
import logging

from dhis2.utils import *


from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.models.dhis2.enum import ValueType
from dhis2_etl.models.dhis2.metadata import *
from dhis2_etl.models.dhis2.type import DHIS2Ref
from dhis2_etl.utils import build_dhis2_id

from . import BaseDHIS2Converter

# Get an instance of a logger
logger = logging.getLogger('openIMIS')
# Create your views here.
# salt = GeneralConfiguration.get_salt()

class CategoryConverter(BaseDHIS2Converter):


    @classmethod
    def to_categories_bundled(cls, objs, categoryName = "", **kwargs):
        return MetadataBundle(\
            categories = [cls.to_categories_obj(objs = objs, categoryName = categoryName, **kwargs)])

    @classmethod
    def to_categories_obj(cls, objs, categoryName = "",   **kwargs):
        #event  = kwargs.get('event',False)
        options = []
        for option in objs:
            options.append(DHIS2Ref(id = build_dhis2_id(getattr(option, 'id'), categoryName)))
        return Category(id = GeneralConfiguration.get_option_set_uid(categoryName),\
                        name = categoryName,\
                        categoryOptions = options,
                        code = categoryName)

    @classmethod
    def to_cat_obj(cls, option, categoryName = "",  att1 = "name", att2 = "",\
         code = 'id', **kwargs):
        if option is not None and hasattr(option, code) and  hasattr(option, att1):
            value = getattr(option, att1)
            if att2 != "":
                value = value + " - " + getattr(option, att2)
            codeStr = getattr(option, code)
            # logger.debug("option code:" + codeStr +"; value:" + value + "for "+ categoryName)
            return CategoryOption(\
                id = build_dhis2_id(codeStr, categoryName),\
                code = codeStr,\
                name = value)
        else:
            return None

    @classmethod
    def to_cat_objs(cls, objs, categoryName = "",  att1 = "name", att2 = "",\
        code = 'id', **kwargs):   
        options = []
        for option in objs:
            options.append(cls.to_option_obj(option  = option,\
                categoryName = categoryName, att1 = att1, att2 = att2, code = code))
        return MetadataBundle( options = options)

