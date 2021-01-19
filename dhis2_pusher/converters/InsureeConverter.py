from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from ..models.dhis2 import *
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2 import utils
import hashlib 
from dict2obj import Dict2Obj
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
insureeProgram =  Dict2Obj(GeneralConfiguration.get_insuree_program())
salt = GeneralConfiguration.get_salt()

class InsureeConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs):
        trackedEntityInstances = []
        logger.debug("start Insuree %d sync",objs.count())
        for insuree in objs:
            trackedEntityInstances.insert(cls.to_tei_obj(insuree))
        return TrackedEntityInstanceBundle(trackedEntityInstances = trackedEntityInstances)

    @classmethod
    def to_tei_obj(cls, insuree):
        if insuree  != None and insuree.uuid != None  and insuree.family != None and insuree.family.uuid != None:
            attributes = []
            # add profession attributes
            if insuree.profession_id != None and is_valid_uid(insureeProgram.profession):
                attributes.insert(AttributeValue(insureeProgram.profession,\
                  GeneralConfiguration.get_profession_code(insuree.profession_id))) 
            # add poverty attributes
            if insuree.poverty_id != None and is_valid_uid(insureeProgram.poverty):
                attributes.insert(AttributeValue(insureeProgram.poverty,\
                  GeneralConfiguration.get_boolean_code(insuree.poverty_id))) 
            #  "CHFId" // duplicate
            # "insuranceId":"g54R38QNwEi", # Salted data for privay reason
            if insuree.chfid != None and is_valid_uid(insureeProgram.insuranceId):
                attributes.insert(AttributeValue(insureeProgram.insuranceId,\
                 hashlib.md5(salt + insuree.chfid).hexdigest())) 
            # "insureeId":"e9fOa40sDwR",  # should not use it
            # "familiyId": attribute ,
            if insuree.familiy.uuid != None and is_valid_uid(insureeProgram.familiy):
                attributes.insert(AttributeValue(insureeProgram.familiy, insuree.familiy.uuid)) 
            # "dob"
            if insuree.dob != None and is_valid_uid(insureeProgram.dob):
                attributes.insert(AttributeValue(insureeProgram.dob, insuree.dob)) 
            #"education"
            if insuree.education_id != None and is_valid_uid(insureeProgram.education):
                attributes.insert(AttributeValue(insureeProgram.education,\
                 GeneralConfiguration.get_education_code(insuree.education_id))) 
            # "groupType",
            if insuree.family.family_type_id != None and is_valid_uid(insureeProgram.groupType):
                attributes.insert(AttributeValue(insureeProgram.groupType,\
                 GeneralConfiguration.get_group_type_code(insuree.family.family_type_id))) 
            # "firstName"
            if insuree.other_name != None and is_valid_uid(insureeProgram.firstName):
                attributes.insert(AttributeValue(insureeProgram.firstName, insuree.other_name)) 
            #"firstServicePoint":"GZ6zgXS25VH",
            if insuree.health_facility.uuid != None and is_valid_uid(insureeProgram.firstServicePoint):
                attributes.insert(AttributeValue(insureeProgram.firstServicePoint,\
                 insuree.health_facility.uuid)) 
            #"gender":
            if insuree.gender_id != None and is_valid_uid(insureeProgram.gender):
                attributes.insert(AttributeValue(insureeProgram.gender,\
                 GeneralConfiguration.get_gender_code(insuree.gender_id))) 
            #"isHead":"siOTMqr9kw6",
            if insuree.head != None and is_valid_uid(insureeProgram.isHead):
                attributes.insert(AttributeValue(insureeProgram.isHead,\
                  GeneralConfiguration.get_boolean_code(insuree.head))) 
            #"identificationId":"MFPEijajdy7", # not used for privacy reason
            #if insuree.passport != None and is_valid_uid(insureeProgram.identificationId):
            #    attributes.insert(AttributeValue(insureeProgram.identificationId, insuree.passport)) 
            #"identificationSource":"jOnARr3GARW", # not used for now
            #if insuree.card_issued  != None and is_valid_uid(insureeProgram.identificationSource):
            #    attributes.insert(AttributeValue(insureeProgram.identificationSource,  GeneralConfiguration.get_identification_source_code(insuree.card_issued_id))) 
            #"maritalSatus":"vncvDog0YwP",
            if insuree.marital != None and is_valid_uid(insureeProgram.maritalSatus):
                attributes.insert(AttributeValue(insureeProgram.maritalSatus,\
                 GeneralConfiguration.get_marital_code(insuree.marital))) 
            #"phoneNumber": "r9hJ7SJbVvx", # TBC
            #if insuree.poverty != None and is_valid_uid(insureeProgram.poverty):
            #attributes.insert(AttributeValue(insureeProgram.poverty, insuree.poverty)) 
            orgUnit = cls.build_dhis2_id(insuree.family.location.uuid)
            trackedEntity = cls.build_dhis2_id(insuree.uuid)
            return TrackedEntityInstance(\
            trackedEntityType = insureeProgram.tieType,\
                trackedEntity = trackedEntity,\
                orgUnit = orgUnit,\
                # add enroment
                enrollments= Enrollment(trackedEntity, trackedEntity, orgUnit, insuree.validity_from),\
                attributes = attributes)
             
        else:
            return None

 
    @classmethod
    def to_enrolment_objs(cls, insurees):
        Enrollments = []
        for insuree in insurees:
            Enrollments.insert(cls.to_enrollment_obj(insuree))
        return EnrollmentBundle(Enrollments)

    @classmethod   
    def to_enrolment_obj(cls, insurees):
        uid = cls.build_dhis2_id(insuree.uuid)
        return Enrollment(uid, uid, cls.build_dhis2_id(insuree.family.location.uuid), insuree.validity_from)

    @classmethod
    def to_event_obj(cls, insureepolicy):
        stageDE = insureeProgram.stage["policy"].dataElements
        dataValue = []
        if is_valid_uid(stageDE.policyStage):
            dataValue.insert(DataValue(stageDE.policyStage,\
                GeneralConfiguration.get_policy_state_code(insureepolicy.policy.stage)))
        if is_valid_uid(stageDE.policyStatus):
            dataValue.insert(DataValue(stageDE.policyStatus,\
                GeneralConfiguration.get_policy_status_code(insureepolicy.policy.status)))
        if is_valid_uid(stageDE.product):
            dataValue.insert(DataValue(stageDE.product,\
                insureepolicy.policy.product.code + " - " + insureepolicy.policy.prodcut.code))
        if is_valid_uid(stageDE.PolicyValue):
            dataValue.insert(DataValue(stageDE.PolicyValue,insureepolicy.policy.value))
        if is_valid_uid(stageDE.expirityDate):
            dataValue.insert(DataValue(stageDE.expirityDate,insureepolicy.policy.expiry_date))
        #event.dataValue.insert(DataValue(stageDE.policyId,cls.build_dhis2_id(insureepolicy.policy.uuid)))
        orgUnit = cls.build_dhis2_id(insureepolicy.insuree.family.location.uuid)
        return Event(\
        program = insureeProgram.id,\
        orgUnit = orgUnit,\
        eventDate = insureepolicy.enrollment_date,\
        status = "COMPLETED",\
        dataValue = dataValue,\
        trackedEntityInstance = cls.build_dhis2_id(insureepolicy.insuree.uuid),\
        programStage = insureeProgram.stage["policy"].id)

        


    @classmethod
    def to_event_objs(cls, insureepolicies):
        Enrollments = [] 
        for insureepolicy in insureepolicies:
            Enrollments.insert(cls.to_enrollment_obj(insureepolicy))
        return EventBundle(Enrollments = Enrollments)

