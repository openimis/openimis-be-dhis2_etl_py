# Copyrights Patrick Delcroix <patrick@pmpd.eu>
# Generic Converter to optionSet
from ..models.dhis2Metadata import OptionInteger, OptionSet, OptionSetBundle, Option, OptionBundle
from ..models.dhis2Type import DHIS2Ref
from ..models.dhis2Enum import ValueType
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2.utils import *
import hashlib 
from ..utils import toDateStr, toDatetimeStr, build_dhis2_id

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
# salt = GeneralConfiguration.get_salt()

class OptionSetConverter(BaseDHIS2Converter):


    @classmethod
    def to_optionsets_bundled(cls, objs, optiontSetName = "",  code = 'id', valueType = ValueType.text, **kwargs):
        return OptionSetBundle(\
            optionSets = [cls.to_optionsets_obj(objs = objs, optiontSetName = optiontSetName\
                , code = code, valueType = valueType)])

    @classmethod
    def to_optionsets_obj(cls, objs, optiontSetName = "",  valueType = ValueType.text, code = 'id', **kwargs):
        #event  = kwargs.get('event',False)
        options = []
        for option in objs:
            options.append(DHIS2Ref(id = build_dhis2_id(getattr(option, code), optiontSetName)))
        return OptionSet(id = GeneralConfiguration.get_option_set_uid(optiontSetName),\
                        name = optiontSetName,\
                        options = options,
                        valueType = valueType)

    @classmethod
    def to_option_obj(cls, option, optiontSetName = "",  att1 = "name", att2 = "",\
         code = 'id', **kwargs):
        if option is not None and hasattr(option, code) and  hasattr(option, att1):
            value = getattr(option, att1)
            if att2 != "":
                value = value + " - " + getattr(option, att2)
            codeStr = getattr(option, code)
            # logger.debug("option code:" + codeStr +"; value:" + value + "for "+ optiontSetName)
            return Option(\
                id = build_dhis2_id(codeStr, optiontSetName),\
                code = codeStr,\
                name = value)
        else:
            return None

    @classmethod
    def to_option_objs(cls, objs, optiontSetName = "",  att1 = "name", att2 = "",\
        code = 'id', **kwargs):   
        options = []
        for option in objs:
            options.append(cls.to_option_obj(option  = option,\
                optiontSetName = optiontSetName, att1 = att1, att2 = att2, code = code))
        return OptionBundle( options = options)

