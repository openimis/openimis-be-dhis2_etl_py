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
from dict2obj import Dict2Obj

claimProgram =  Dict2Obj(GeneralConfiguration.get_claim_program())
salt = GeneralConfiguration.get_salt()
CLAIM_REJECTED = 1
CLAIM_ENTERED = 2
CLAIM_CHECKED = 4
CLAIM_PROCESSED = 8
CLAIM_VALUATED = 16

class ClaimConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs):
        bundle = TrackedEntityInstanceBundle()
        for claim in objs:
            bundle.trackedEntityInstances.insert(cls.to_tei_obj(claim))
        return bundle

    @classmethod
    def to_tei_objs(cls, claim):
        if claim  != None and claim.insuree != None and claim.insuree.uuid != None:
            tei = TrackedEntityInstance()
            tei.trackedEntityType = claimProgram.tieType
            tei.trackedEntity = cls.build_dhis2_id(claim.uuid)
            tei.orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
            # add enroment
            enrollment = Enrollment(tei.trackedEntity, tei.trackedEntity,\
                 tei.orgUnit, claim.date_claimed)
            if claimProgram.stage["claimDetails"] != None :
                enrollment.events.insert(cls.to_event_obj(claim)) # add claim details
            if claimProgram.stage["items"] != None :
                for service in claim.services: 
                    enrollment.events.insert(cls.to_event_item_obj(service)) # add claim items
            if claimProgram.stage["services"] != None :
                for items in claim.items: 
                    enrollment.events.insert(cls.to_event_service_obj(items)) # add claim service
            tei.enrollments.insert( )
            # add insuranceID attributes
            if claim.insuree != None and claim.insuree.chfid != None and is_valid_uid(claimProgram.insuranceId):
                    tei.attributes.insert(AttributeValue(claimProgram.insuranceId,\
                    hashlib.md5(salt + claim.insuree.chfid).hexdigest())) 
            # claimAdministrator
            if claim.admin  != None and claim.admin.uuid  != None and is_valid_uid(claimProgram.claimAdministrator):
                    tei.attributes.insert(AttributeValue(claimProgram.claimAdministrator,\
                    claim.admin.uuid)) 
            #    "claimNumber"
            if claim.code  != None and is_valid_uid(claimProgram.claimNumber):
                    tei.attributes.insert(AttributeValue(claimProgram.claimNumber,\
                    claim.code)) 
            #    "diagnoseMain"
            if claim.icd  != None and is_valid_uid(claimProgram.diagnoseMain):
                    tei.attributes.insert(AttributeValue(claimProgram.diagnoseMain,\
                    claim.icd.code + " - " + claim.icd.name))
            #    "diagnoseSec1"
            if claim.icd_1  != None and is_valid_uid(claimProgram.diagnoseSec1):
                    tei.attributes.insert(AttributeValue(claimProgram.diagnoseSec1,\
                    claim.icd_1.code + " - " + claim.icd_1.name))
            #    "diagnoseSec2"
            if claim.icd_2  != None and is_valid_uid(claimProgram.diagnoseSec2):
                    tei.attributes.insert(AttributeValue(claimProgram.diagnoseSec2,\
                    claim.icd_2.code + " - " + claim.icd_2.name))
            #    "diagnoseSec3"
            if claim.icd_3  != None and is_valid_uid(claimProgram.diagnoseSec3):
                    tei.attributes.insert(AttributeValue(claimProgram.diagnoseSec3,\
                    claim.icd_3.code + " - " + claim.icd_3.name))
            #    "diagnoseSec4"
            if claim.icd_4  != None and is_valid_uid(claimProgram.diagnoseSec4):
                    tei.attributes.insert(AttributeValue(claimProgram.diagnoseSec4,\
                    claim.icd_4.code + " - " + claim.icd_4.name))
            #    "VisitType"
            if claim.visit_type  != None and is_valid_uid(claimProgram.VisitType):
                    tei.attributes.insert(AttributeValue(claimProgram.VisitType,\
                    claim.visit_type ))
            return tei
        else:
            return None

 
    @classmethod
    def to_enrolment_objs(cls, claims):
        bundle = EnrollmentBundle()
        for claim in claims:
            bundle.Enrollments.insert(cls.to_enrollment_obj(claim))
        return bundle

    @classmethod   
    def to_enrolment_obj(cls, claims):
        uid = cls.build_dhis2_id(insuree.uuid)
        return Enrollment(uid, uid, cls.build_dhis2_id(claim.health_facility.uuid), claim.date_claimed)

    @classmethod
    def to_event_obj(cls, claim):
        # add claim details event
        event = Event()
        event.program = claimProgram.id
        event.orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        event.eventDate = claim.date_from 
        event.status = "COMPLETED"
        event.dataValue = []
        event.trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        event.programStage = claimProgram.stage["claimDetails"].id
        stageDE = claimProgram.stage["claimDetails"].data
        # "status"
        if is_valid_uid(stageDE.status):
            event.dataValue.insert(DataValue(stageDE.status,\
                GeneralConfiguration.get_policy_state_code(claim.status)))
        # "amount"
        if is_valid_uid(stageDE.amount):
            event.dataValue.insert(DataValue(stageDE.amount, claim.claimed ))
        # "checkedDate"
        if is_valid_uid(stageDE.checkedDate):
            event.dataValue.insert(DataValue(stageDE.checkedDate, claim.date_claimed ))
        # "processedDate"
        if is_valid_uid(stageDE.processedDate) and claim.process_stamp != None:
            event.dataValue.insert(DataValue(stageDE.processedDate,\
             claim.process_stamp.date()))
        # "adjustedDate"
        if is_valid_uid(stageDE.adjustedDate) and claim.submit_stamp != None:
            event.dataValue.insert(DataValue(stageDE.adjustedDate, \
                claim.submit_stamp.date()))
        if (claim.status == CLAIM_VALUATED or claim.status == CLAIM_PROCESSED):
            # "adjustedAmount"
            if is_valid_uid(stageDE.adjustedAmount) and claim.valuated!= None :
                event.dataValue.insert(DataValue(stageDE.adjustedAmount,\
                 claim.valuated ))
            # "valuationDate" # FIXME not correct in case of batch run
            if is_valid_uid(stageDE.valuationDate):
                event.dataValue.insert(DataValue(stageDE.valuationDate, \
                    max(claim.submit_stamp.date(),claim.process_stamp.date(),claim.validity_from)))
            # "approvedAmount":"TiZrzsT8088",
            if is_valid_uid(stageDE.approvedAmount) and claim.approved != None :
                event.dataValue.insert(DataValue(stageDE.approvedAmount, \
                    claim.approved ))
            # "valuatedAmount":"Fk7sSgbFTaG",
            if is_valid_uid(stageDE.valuatedAmount) and claim.valuated != None:
                event.dataValue.insert(DataValue(stageDE.valuatedAmount, \
                    claim.valuated))
            # "renumeratedAmount":""
            if is_valid_uid(stageDE.renumeratedAmount)and claim.reinsured != None:
                event.dataValue.insert(DataValue(stageDE.renumeratedAmount, \
                    claim.reinsured))
        # "rejectionDate"
        elif (claim.status == CLAIM_REJECTED ) and is_valid_uid(stageDE.rejectionDate):
            event.dataValue.insert(DataValue(stageDE.rejectionDate,\
                max(claim.submit_stamp.date(),claim.process_stamp.date())))


    @classmethod
    def to_event_item_obj(cls, item):
        event = Event()
        event.program = claimProgram.id
        event.orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        event.eventDate = claim.date_from 
        event.status = "COMPLETED"
        event.dataValue = []
        event.trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        event.programStage = claimProgram.stage["items"].id
        stageDE = claimProgram.stage["items"].data
        #"item":"VFWCqLKPuSd",
        if is_valid_uid(stageDE.item)and item.item != None:
                event.dataValue.insert(DataValue(stageDE.item, \
                    item.item.code + " - " + item.item.name))
        #"quantity":"xBdXypAmk7V", # 
        if is_valid_uid(stageDE.quantity)and claim.qty_provided != None:
                event.dataValue.insert(DataValue(stageDE.quantity, \
                    item.qty_provided)) 
        #"price":"Gu1DbTMoVGx",
        if is_valid_uid(stageDE.price)and item.price != None:
                event.dataValue.insert(DataValue(stageDE.price, \
                    item.price_asked))
        #"deductibleAmount":"uWJD6i5xf6A",
        if is_valid_uid(stageDE.deductibleAmount)and item.deductable_amount  != None:
                event.dataValue.insert(DataValue(stageDE.deductibleAmount, \
                    item.deductable_amount ))
        #"exeedingCeilingAmount":"krBi9DbQl4Y",
        if is_valid_uid(stageDE.exeedingCeilingAmount )and item.exceed_ceiling_amount  != None:
                event.dataValue.insert(DataValue(stageDE.exeedingCeilingAmount , \
                    item.exceed_ceiling_amount ))
        #"renumeratedAmount":"WyAw53dfnMj", # not used
        if is_valid_uid(stageDE.renumeratedAmount)and item.remunerated_amount  != None:
                event.dataValue.insert(DataValue(stageDE.renumeratedAmount, \
                    item.remunerated_amount ))
        #"seqId":"QmuynKAhycW" # same Service
        #if is_valid_uid(stageDE.renumeratedAmount)and item.reinsured != None:
        #        event.dataValue.insert(DataValue(stageDE.renumeratedAmount, \
        #            item.reinsured))        

    @classmethod
    def to_event_service_obj(cls, service):
        event = Event()
        event.program = claimProgram.id
        event.orgUnit = cls.build_dhis2_id(claim.health_facility.uuid)
        event.eventDate = claim.date_from 
        event.status = "COMPLETED"
        event.dataValue = []
        event.trackedEntityInstance = cls.build_dhis2_id(claim.uuid)
        event.programStage = claimProgram.stage["services"].id
        stageDE = claimProgram.stage["services"].data
        #"adjustedAmount"not used
        if is_valid_uid(stageDE.adjustedAmount)and service.price_adjusted   != None:
                event.dataValue.insert(DataValue(stageDE.adjustedAmount, \
                    service.price_adjusted  ))
        #"approvedAmount" # not used
        if is_valid_uid(stageDE.approvedAmount)and service.price_approved   != None:
                event.dataValue.insert(DataValue(stageDE.approvedAmount, \
                    service.price_approved  ))
        #"valuatedAmount" # not used
        if is_valid_uid(stageDE.valuatedAmount)and service.remunerated_amount  != None:
                event.dataValue.insert(DataValue(stageDE.valuatedAmount, \
                    service.remunerated_amount ))
        #"service":
        if is_valid_uid(stageDE.service)and service.service != None:
                event.dataValue.insert(DataValue(stageDE.service, \
                    service.service.code + " - " + service.service.name))
        #"quantity":,
        if is_valid_uid(stageDE.quantity)and service.qty_provided != None:
                event.dataValue.insert(DataValue(stageDE.quantity, \
                    service.qty_provided)) 
        #"price":"uwGg814hDhB",
        if is_valid_uid(stageDE.price)and service.price != None:
                event.dataValue.insert(DataValue(stageDE.price, \
                    service.price_asked))
        #"deductibleAmount"
        if is_valid_uid(stageDE.deductibleAmount)and service.deductable_amount  != None:
                event.dataValue.insert(DataValue(stageDE.deductibleAmount, \
                    service.deductable_amount ))
        #"exeedingCeilingAmount"
        if is_valid_uid(stageDE.exeedingCeilingAmount )and service.exceed_ceiling_amount  != None:
                event.dataValue.insert(DataValue(stageDE.exeedingCeilingAmount , \
                    service.exceed_ceiling_amount ))
        #"renumeratedAmount": # not used
        if is_valid_uid(stageDE.renumeratedAmount)and service.remunerated_amount  != None:
                event.dataValue.insert(DataValue(stageDE.renumeratedAmount, \
                    service.remunerated_amount ))
        #"seqId":"QmuynKAhycW"
        #if is_valid_uid(stageDE.renumeratedAmount)and service.reinsured != None:
        #        event.dataValue.insert(DataValue(stageDE.renumeratedAmount, \
        #            service.reinsured)) 
    @classmethod
    def to_event_objs(cls, insureepolicies):
        bundle = EventBundle()
        for claim in insurees:
            bundle.Enrollments.insert(cls.to_enrollment_obj(claim))
        return bundle

