from contribution.models import Premium
from product.models import Product
from ..models.dhis2Program import *
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
fundingProgram = GeneralConfiguration.get_funding_program()
locationConfig = GeneralConfiguration.get_location()

class FundingConverter(BaseDHIS2Converter):

    @classmethod
    def to_event_obj(cls, funding, **kwargs):
        stageDE = fundingProgram.get('stages').get('funding').get('dataElements')
        dataValues = []
        if is_valid_uid(stageDE.get('product')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('product'),\
                value = funding.policy.product_id))
        if is_valid_uid(stageDE.get('amount')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('amount'),\
                value = funding.amount))        

        return Event(\
            event = build_dhis2_id(funding.id, 'funding'),\
            program = fundingProgram['id'],\
            orgUnit = locationConfig['rootOrgUnit'],\
            eventDate = toDateStr(funding.pay_date), \
            status = "COMPLETED",\
            dataValues = dataValues,\
            programStage = fundingProgram.get('stages').get('funding').get('id'))


    @classmethod
    def to_event_objs(cls, fundings, **kwargs):
        events = [] 
        for funding in fundings:
            events.append(cls.to_event_obj(funding))
        return EventBundle(events = events)

