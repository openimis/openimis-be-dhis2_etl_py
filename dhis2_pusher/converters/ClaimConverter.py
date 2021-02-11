from claim.models import Claim, ClaimItem, ClaimService
from medical.models import Diagnosis, Item, Service
from insuree.models import Insuree, InsureePolicy
from policy.models import Policy
from product.models import ProductItem, ProductService
from .. import models
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2 import utils
import hashlib 
from ..models.dhis2 import *
from ..utils import toDateStr, toDatetimeStr, build_dhis2_id

claimProgram =  GeneralConfiguration.get_claim_program()
salt = GeneralConfiguration.get_salt()
CLAIM_REJECTED = 1
CLAIM_ENTERED = 2
CLAIM_CHECKED = 4
CLAIM_PROCESSED = 8
CLAIM_VALUATED = 16

class ClaimConverter(BaseDHIS2Converter):


    @classmethod
    def to_enrolment_obj(cls, claims, **kwargs):
        if claim is not None and claim.insuree is not None and claim.insuree.uuid is not None:
            trackedEntity = build_dhis2_id(claim.insuree.uuid)
            uid = build_dhis2_id(claim.uuid)
            orgUnit = build_dhis2_id(claim.health_facility.uuid)
            attributes = []
            # claimAdministrator
            if claim.admin is not None and claim.admin.uuid is not None and is_valid_uid(claimProgram['attributes']['claimAdministrator']):
                    attributes.append(AttributeValue(attribute = claimProgram['attributes']['claimAdministrator'],\
                    value = claim.admin.uuid)) 
            #    "claimNumber"
            if claim.code is not None and is_valid_uid(claimProgram['attributes']['claimNumber']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['claimNumber'],\
                    value = claim.code)) 
            #    "diagnoseMain"
            if claim.icd is not None and is_valid_uid(claimProgram['attributes']['diagnoseMain']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['diagnoseMain'],\
                    value = claim.icd.code + " - " + claim.icd.name))
            #    "diagnoseSec1"
            if claim.icd_1 is not None and is_valid_uid(claimProgram['attributes']['diagnoseSec1']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['diagnoseSec1'],\
                    value = claim.icd_1.code + " - " + claim.icd_1.name))
            #    "diagnoseSec2"
            if claim.icd_2 is not None and is_valid_uid(claimProgram['attributes']['diagnoseSec2']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['diagnoseSec2'],\
                    value = claim.icd_2.code + " - " + claim.icd_2.name))
            #    "diagnoseSec3"
            if claim.icd_3 is not None and is_valid_uid(claimProgram['attributes']['diagnoseSec3']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['diagnoseSec3'],\
                    value = claim.icd_3.code + " - " + claim.icd_3.name))
            #    "diagnoseSec4"
            if claim.icd_4 is not None and is_valid_uid(claimProgram['attributes']['diagnoseSec4']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['diagnoseSec4'],\
                    value = claim.icd_4.code + " - " + claim.icd_4.name))
            #    "VisitType"
            if claim.visit_type is not None and is_valid_uid(claimProgram['attributes']['VisitType']):
                    attributes.append(AttributeValue( attribute = claimProgram['attributes']['VisitType'],\
                    value = claim.visit_type ))
             # add enroment
            events = []
            if event:
                if claimProgram['stages']['claimDetails'] is not None :
                    events.append(cls.to_event_obj(claim, claim = claim)) # add claim details
                if claimProgram['stages']['items'] is not None :
                    for service in claim.services: 
                        events.append(cls.to_event_item_obj(service, claim = claim)) # add claim items
                if claimProgram['stages']['services'] is not None :
                    for items in claim.items: 
                        events.append(cls.to_event_service_obj(items)) # add claim service
            return Enrollment(enrollment = uid, trackedEntityInstance = trackedEntity,\
              incidentDate = toDateStr(claim.date_claimed),enrollmentDate = toDateStr(claim.date_claimed),\
              orgUnit = orgUnit, status = "COMPLETED",program = claimProgram['id'],\
                  attributes = attributes,  events = events )
        else:
            return None

 
    @classmethod
    def to_enrolment_objs(cls, claims, **kwargs):
        Enrollments = []
        for claim in claims:
            Enrollments.append(cls.to_enrollment_obj(claim))
        return  EnrollmentBundle(Enrollments = Enrollments)

    @classmethod
    def to_event_obj(cls, claim, **kwargs):
        # add claim details event
        stageDE = claimProgram['stages']['claimDetails']['dataElements']
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = build_dhis2_id(claim.uuid)
        dataValue = []
        # "status"
        if is_valid_uid(stageDE['status']):
            dataValue.append(EventDataValue(dataElement = stageDE['status'],\
                value = GeneralConfiguration.get_claim_status_code(claim.status)))
        # "amount"
        if is_valid_uid(stageDE['amount']):
            dataValue.append(EventDataValue(dataElement = stageDE['amount'], value = claim.claimed ))
        # "checkedDate"
        if is_valid_uid(stageDE['checkedDate']):
                dataValue.append(EventDataValue(dataElement = stageDE['checkedDate'], value = toDateStr(claim.date_claimed) ))
        # "processedDate"
        if is_valid_uid(stageDE['processedDate']) and claim.process_stamp is not None:
            dataValue.append(EventDataValue(dataElement = stageDE['processedDate'],\
                value = toDateStr(claim.process_stamp)))
        # "adjustedDate"
        if is_valid_uid(stageDE['adjustedDate']) and claim.submit_stamp is not None:
            dataValue.append(EventDataValue(dataElement = stageDE['adjustedDate'], \
                value = toDateStr(claim.submit_stamp)))
        if (claim.status == CLAIM_VALUATED or claim.status == CLAIM_PROCESSED):
            # "adjustedAmount"
            if is_valid_uid(stageDE['adjustedAmount']) and claim.valuated is not None :
                dataValue.append(EventDataValue(dataElement = stageDE['adjustedAmount'],\
                    value = claim.valuated ))
            # "valuationDate" # FIXME not correct in case of batch run
            if is_valid_uid(stageDE['valuationDate']):
                if claim.process_stamp is not None:
                    dateEvent = claim.process_stamp.date()
                else:
                    dateEvent = claim.submit_stamp.date()
                dataValue.append(EventDataValue(dataElement = stageDE['valuationDate'], \
                    value =  toDateStr(dateEvent)))
            # "approvedAmount":"TiZrzsT8088",
            if is_valid_uid(stageDE['approvedAmount']) and claim.approved is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['approvedAmount'], \
                    value = claim.approved ))
            # "valuatedAmount":"Fk7sSgbFTaG",
            if is_valid_uid(stageDE['valuatedAmount']) and claim.valuated is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['valuatedAmount'], \
                    value = claim.valuated))
            # "renumeratedAmount":""
            if is_valid_uid(stageDE['renumeratedAmount'])and claim.reinsured is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['renumeratedAmount'], \
                    value = claim.reinsured))
        # "rejectionDate"
        elif (claim.status == CLAIM_REJECTED ) and is_valid_uid(stageDE['rejectionDate']):
            if claim.process_stamp is not None:
                dateEvent = claim.process_stamp.date()
            else:
                dateEvent = claim.submit_stamp.date()


            dataValue.append(EventDataValue(dataElement = stageDE['rejectionDate'],\
                value = toDateStr(dateEvent)))
        return Event(\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateTimeStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram['stages']['claimDetails']['id'])




    @classmethod
    def to_event_item_obj(cls, item,  **kwargs):
        claim  = kwargs.get('claim',item.claim)
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = build_dhis2_id(claim.insuree.uuid)
        stageDE = claimProgram['stages']['items']['dataElements']
        dataValue = []
        #"item":"VFWCqLKPuSd",
        if is_valid_uid(stageDE['item'])and item.item is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['item'], \
                    value = item.item.code + " - " + item.item.name))
        #"quantity":"xBdXypAmk7V", # 
        if is_valid_uid(stageDE['quantity'])and item.qty_provided is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['quantity'], \
                    value = item.qty_provided)) 
        #"price":"Gu1DbTMoVGx",
        if is_valid_uid(stageDE['price'])and item.price is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['price'], \
                    value = item.price_asked))
        #"deductibleAmount":"uWJD6i5xf6A",
        if is_valid_uid(stageDE['deductibleAmount'])and item.deductable_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['deductibleAmount'], \
                    value = item.deductable_amount ))
        #"exeedingCeilingAmount":"krBi9DbQl4Y",
        if is_valid_uid(stageDE['exeedingCeilingAmount'] )and item.exceed_ceiling_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['exeedingCeilingAmount'] , \
                    value = item.exceed_ceiling_amount ))
        #"renumeratedAmount":"WyAw53dfnMj", # not used
        if is_valid_uid(stageDE['renumeratedAmount'])and item.remunerated_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['renumeratedAmount'], \
                    value = item.remunerated_amount ))
        #"seqId":"QmuynKAhycW" # same Service
        #if is_valid_uid(stageDE['renumeratedAmount'])and item.reinsured is not None:
        #        dataValue.append(EventDataValue(dataElement = stageDE['renumeratedAmount'], \
        #            item.reinsured))     
        event = Event(\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateTimeStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram['stages']['items']['id'])
           

    @classmethod
    def to_event_service_obj(cls, service ,  **kwargs):
        claim  = kwargs.get('claim',service.claim)
        trackedEntityInstance = build_dhis2_id(claim.insuree.uuid)
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        stageDE = claimProgram['stages']['services']['dataElements']
        dataValue = []
        #"adjustedAmount"not used
        if is_valid_uid(stageDE['adjustedAmount'])and service.price_adjusted is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['adjustedAmount'], \
                    value = service.price_adjusted  ))
        #"approvedAmount" # not used
        if is_valid_uid(stageDE['approvedAmount'])and service.price_approved is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['approvedAmount'], \
                    value = service.price_approved  ))
        #"valuatedAmount" # not used
        if is_valid_uid(stageDE['valuatedAmount'])and service.remunerated_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['valuatedAmount'], \
                    value = service.remunerated_amount ))
        #"service":
        if is_valid_uid(stageDE['service'])and service.service is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['service'], \
                    value = service.service.code + " - " + service.service.name))
        #"quantity":,
        if is_valid_uid(stageDE['quantity'])and service.qty_provided is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['quantity'], \
                    value = service.qty_provided)) 
        #"price":"uwGg814hDhB",
        if is_valid_uid(stageDE['price'])and service.price is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['price'], \
                    value = service.price_asked))
        #"deductibleAmount"
        if is_valid_uid(stageDE['deductibleAmount'])and service.deductable_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['deductibleAmount'], \
                    value = service.deductable_amount ))
        #"exeedingCeilingAmount"
        if is_valid_uid(stageDE['exeedingCeilingAmount'] )and service.exceed_ceiling_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['exeedingCeilingAmount'] , \
                    value = service.exceed_ceiling_amount ))
        #"renumeratedAmount": # not used
        if is_valid_uid(stageDE['renumeratedAmount'])and service.remunerated_amount is not None:
                dataValue.append(EventDataValue(dataElement = stageDE['renumeratedAmount'], \
                    value = service.remunerated_amount ))
        #"seqId":"QmuynKAhycW"
        #if is_valid_uid(stageDE['renumeratedAmount'])and service.reinsured is not None:
        #        dataValue.append(EventDataValue(dataElement = stageDE['renumeratedAmount'], \
        #            service.reinsured)) 
        return Event(\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram['stages']['services']['id'])
        
        
    @classmethod
    def to_event_objs(cls, claims, **kwargs):
        Enrollments =[]
        for claim in claims:
            Enrollments.append(cls.to_enrollment_obj(claim))
        return EventBundle(Enrollments)

