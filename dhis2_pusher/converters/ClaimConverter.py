from claim.models import Claim, ClaimItem, ClaimService
from medical.models import Diagnosis, Item, Service
from insuree.models import InsureePolicy
from policy.models import Policy
from product.models import ProductItem, ProductService
from .. import models
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2 import utils
import hashlib 
from ..models.dhis2 import *

claimProgram =  GeneralConfiguration.get_claim_program()
salt = GeneralConfiguration.get_salt()
CLAIM_REJECTED = 1
CLAIM_ENTERED = 2
CLAIM_CHECKED = 4
CLAIM_PROCESSED = 8
CLAIM_VALUATED = 16

class ClaimConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs):
        trackedEntityInstances = []
        for claim in objs:
            trackedEntityInstances.append(cls.to_tei_obj(claim))
        return TrackedEntityInstanceBundle(trackedEntityInstances = trackedEntityInstances)

    @classmethod
    def to_tei_objs(cls, claim):
        if claim  != None and claim.insuree != None and claim.insuree.uuid != None:
            trackedEntity = cls.build_dhis2_id(claim.uuid)
            orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
            attributes = []
            # add insuranceID attributes
            if claim.insuree != None and claim.insuree.chfid != None and is_valid_uid(claimProgram.attributes.insuranceId):
                    attributes.append(AttributeValue(attribute = claimProgram.attributes.insuranceId,\
                    value = hashlib.md5((salt + claim.insuree.chfid).encode('utf-8')).hexdigest())) 
            # claimAdministrator
            if claim.admin  != None and claim.admin.uuid  != None and is_valid_uid(claimProgram.attributes.claimAdministrator):
                    attributes.append(AttributeValue(attribute = claimProgram.attributes.claimAdministrator,\
                    value = claim.admin.uuid)) 
            #    "claimNumber"
            if claim.code  != None and is_valid_uid(claimProgram.attributes.claimNumber):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.claimNumber,\
                    value = claim.code)) 
            #    "diagnoseMain"
            if claim.icd  != None and is_valid_uid(claimProgram.attributes.diagnoseMain):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.diagnoseMain,\
                    value = claim.icd.code + " - " + claim.icd.name))
            #    "diagnoseSec1"
            if claim.icd_1  != None and is_valid_uid(claimProgram.attributes.diagnoseSec1):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.diagnoseSec1,\
                    value = claim.icd_1.code + " - " + claim.icd_1.name))
            #    "diagnoseSec2"
            if claim.icd_2  != None and is_valid_uid(claimProgram.attributes.diagnoseSec2):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.diagnoseSec2,\
                    value = claim.icd_2.code + " - " + claim.icd_2.name))
            #    "diagnoseSec3"
            if claim.icd_3  != None and is_valid_uid(claimProgram.attributes.diagnoseSec3):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.diagnoseSec3,\
                    value = claim.icd_3.code + " - " + claim.icd_3.name))
            #    "diagnoseSec4"
            if claim.icd_4  != None and is_valid_uid(claimProgram.attributes.diagnoseSec4):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.diagnoseSec4,\
                    value = claim.icd_4.code + " - " + claim.icd_4.name))
            #    "VisitType"
            if claim.visit_type  != None and is_valid_uid(claimProgram.attributes.VisitType):
                    attributes.append(AttributeValue( attribute = claimProgram.attributes.VisitType,\
                    value = claim.visit_type ))
             # add enroment
            enrollment = Enrollment(trackedEntity, trackedEntity,\
                 orgUnit, claim.date_claimed)
            if claimProgram.stage["claimDetails"] != None :
                enrollment.events.append(cls.to_event_obj(claim)) # add claim details
            if claimProgram.stage["items"] != None :
                for service in claim.services: 
                    enrollment.events.append(cls.to_event_item_obj(service)) # add claim items
            if claimProgram.stage["services"] != None :
                for items in claim.items: 
                    enrollment.events.append(cls.to_event_service_obj(items)) # add claim service
            return TrackedEntityInstance(\
                trackedEntityType = claimProgram.tieType,\
                trackedEntity = trackedEntity,\
                orgUnit = orgUnit,\
                enrollments = enrollments)
        else:
            return None

 
    @classmethod
    def to_enrolment_objs(cls, claims):
        Enrollments = []
        for claim in claims:
            Enrollments.append(cls.to_enrollment_obj(claim))
        return  EnrollmentBundle(Enrollments = Enrollments)

    @classmethod   
    def to_enrolment_obj(cls, claims):
        uid = cls.build_dhis2_id(insuree.uuid)
        return Enrollment(uid, uid, cls.build_dhis2_id(claim.health_facility.uuid), claim.date_claimed)

    @classmethod
    def to_event_obj(cls, claim):
        # add claim details event
        stageDE = claimProgram.stage["claimDetails"].dataElements
        orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        dataValue = []
        # "status"
        if is_valid_uid(stageDE.status):
            dataValue.append(EventDataValue(dataElement = stageDE.status,\
                value = GeneralConfiguration.get_policy_state_code(claim.status)))
        # "amount"
        if is_valid_uid(stageDE.amount):
            dataValue.append(EventDataValue(dataElement = stageDE.amount, value = claim.claimed ))
        # "checkedDate"
        if is_valid_uid(stageDE.checkedDate):
                dataValue.append(EventDataValue(dataElement = stageDE.checkedDate, value = claim.date_claimed ))
        # "processedDate"
        if is_valid_uid(stageDE.processedDate) and claim.process_stamp != None:
            dataValue.append(EventDataValue(dataElement = stageDE.processedDate,\
                value = claim.process_stamp.date()))
        # "adjustedDate"
        if is_valid_uid(stageDE.adjustedDate) and claim.submit_stamp != None:
            dataValue.append(EventDataValue(dataElement = stageDE.adjustedDate, \
                value = claim.submit_stamp.date()))
        if (claim.status == CLAIM_VALUATED or claim.status == CLAIM_PROCESSED):
            # "adjustedAmount"
            if is_valid_uid(stageDE.adjustedAmount) and claim.valuated!= None :
                dataValue.append(EventDataValue(dataElement = stageDE.adjustedAmount,\
                    value = claim.valuated ))
            # "valuationDate" # FIXME not correct in case of batch run
            if is_valid_uid(stageDE.valuationDate):
                dataValue.append(EventDataValue(dataElement = stageDE.valuationDate, \
                    value =  max(claim.submit_stamp.date(),claim.process_stamp.date(),claim.validity_from)))
            # "approvedAmount":"TiZrzsT8088",
            if is_valid_uid(stageDE.approvedAmount) and claim.approved != None :
                dataValue.append(EventDataValue(dataElement = stageDE.approvedAmount, \
                    value = claim.approved ))
            # "valuatedAmount":"Fk7sSgbFTaG",
            if is_valid_uid(stageDE.valuatedAmount) and claim.valuated != None:
                dataValue.append(EventDataValue(dataElement = stageDE.valuatedAmount, \
                    value = claim.valuated))
            # "renumeratedAmount":""
            if is_valid_uid(stageDE.renumeratedAmount)and claim.reinsured != None:
                dataValue.append(EventDataValue(dataElement = stageDE.renumeratedAmount, \
                    value = claim.reinsured))
        # "rejectionDate"
        elif (claim.status == CLAIM_REJECTED ) and is_valid_uid(stageDE.rejectionDate):
            dataValue.append(EventDataValue(dataElement = stageDE.rejectionDate,\
                value = max(claim.submit_stamp.date(),claim.process_stamp.date())))
        return Event(\
            program = claimProgram.id,\
            orgUnit = orgUnit,\
            eventDate = claim.date_from ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.stage["claimDetails"].id)




    @classmethod
    def to_event_item_obj(cls, item):
        orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        stageDE = claimProgram.stage["items"].dataElements
        dataValue = []
        #"item":"VFWCqLKPuSd",
        if is_valid_uid(stageDE.item)and item.item != None:
                dataValue.append(EventDataValue(dataElement = stageDE.item, \
                    value = item.item.code + " - " + item.item.name))
        #"quantity":"xBdXypAmk7V", # 
        if is_valid_uid(stageDE.quantity)and claim.qty_provided != None:
                dataValue.append(EventDataValue(dataElement = stageDE.quantity, \
                    value = item.qty_provided)) 
        #"price":"Gu1DbTMoVGx",
        if is_valid_uid(stageDE.price)and item.price != None:
                dataValue.append(EventDataValue(dataElement = stageDE.price, \
                    value = item.price_asked))
        #"deductibleAmount":"uWJD6i5xf6A",
        if is_valid_uid(stageDE.deductibleAmount)and item.deductable_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.deductibleAmount, \
                    value = item.deductable_amount ))
        #"exeedingCeilingAmount":"krBi9DbQl4Y",
        if is_valid_uid(stageDE.exeedingCeilingAmount )and item.exceed_ceiling_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.exeedingCeilingAmount , \
                    value = item.exceed_ceiling_amount ))
        #"renumeratedAmount":"WyAw53dfnMj", # not used
        if is_valid_uid(stageDE.renumeratedAmount)and item.remunerated_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.renumeratedAmount, \
                    value = item.remunerated_amount ))
        #"seqId":"QmuynKAhycW" # same Service
        #if is_valid_uid(stageDE.renumeratedAmount)and item.reinsured != None:
        #        dataValue.append(EventDataValue(dataElement = stageDE.renumeratedAmount, \
        #            item.reinsured))     
        event = Event(\
            program = claimProgram.id,\
            orgUnit = orgUnit,\
            eventDate = claim.date_from ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.stage["items"].id)
           

    @classmethod
    def to_event_service_obj(cls, service):
        trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        stageDE = claimProgram.stage["services"].dataElements
        dataValue = []
        #"adjustedAmount"not used
        if is_valid_uid(stageDE.adjustedAmount)and service.price_adjusted   != None:
                dataValue.append(EventDataValue(dataElement = stageDE.adjustedAmount, \
                    value = service.price_adjusted  ))
        #"approvedAmount" # not used
        if is_valid_uid(stageDE.approvedAmount)and service.price_approved   != None:
                dataValue.append(EventDataValue(dataElement = stageDE.approvedAmount, \
                    value = service.price_approved  ))
        #"valuatedAmount" # not used
        if is_valid_uid(stageDE.valuatedAmount)and service.remunerated_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.valuatedAmount, \
                    value = service.remunerated_amount ))
        #"service":
        if is_valid_uid(stageDE.service)and service.service != None:
                dataValue.append(EventDataValue(dataElement = stageDE.service, \
                    value = service.service.code + " - " + service.service.name))
        #"quantity":,
        if is_valid_uid(stageDE.quantity)and service.qty_provided != None:
                dataValue.append(EventDataValue(dataElement = stageDE.quantity, \
                    value = service.qty_provided)) 
        #"price":"uwGg814hDhB",
        if is_valid_uid(stageDE.price)and service.price != None:
                dataValue.append(EventDataValue(dataElement = stageDE.price, \
                    value = service.price_asked))
        #"deductibleAmount"
        if is_valid_uid(stageDE.deductibleAmount)and service.deductable_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.deductibleAmount, \
                    value = service.deductable_amount ))
        #"exeedingCeilingAmount"
        if is_valid_uid(stageDE.exeedingCeilingAmount )and service.exceed_ceiling_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.exeedingCeilingAmount , \
                    value = service.exceed_ceiling_amount ))
        #"renumeratedAmount": # not used
        if is_valid_uid(stageDE.renumeratedAmount)and service.remunerated_amount  != None:
                dataValue.append(EventDataValue(dataElement = stageDE.renumeratedAmount, \
                    value = service.remunerated_amount ))
        #"seqId":"QmuynKAhycW"
        #if is_valid_uid(stageDE.renumeratedAmount)and service.reinsured != None:
        #        dataValue.append(EventDataValue(dataElement = stageDE.renumeratedAmount, \
        #            service.reinsured)) 
        return Event(\
            program = claimProgram.id,\
            orgUnit = orgUnit,\
            eventDate = claim.date_from ,\
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.stage["services"].id)
        
        
    @classmethod
    def to_event_objs(cls, insureepolicies):
        Enrollments =[]
        for claim in insurees:
            Enrollments.append(cls.to_enrollment_obj(claim))
        return EventBundle(Enrollments)

