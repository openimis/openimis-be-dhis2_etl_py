from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from . import models
from .configuration import GeneralConfiguration
from dhis2 import utils
import hashlib 

insureeProgram =  GeneralConfiguration.get_insuree_program()
salt = GeneralConfiguration.get_salt()
class InsureeConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs):
        bundle = TrackedEntityInstanceBundle()
        for insuree in objs:
            bundle.trackedEntityInstances.insert(cls.to_tei_obj(insuree))
        return bundle

    @classmethod
    def to_tei_objs(cls, insuree):
        if insuree  != None and insuree.uuid != None  and insuree.family != None and insuree.family.uuid != None:
            tei = TrackedEntityInstance()
            tei.trackedEntityType = insureeProgram.tieType
            tei.trackedEntity = cls.build_dhis2_id(insuree.uuid)
            tei.orgUnit = cls.build_dhis2_id(insuree.family.location.uuid)
            # add enroment
            tei.enrollments.insert( Enrollment(tei.trackedEntity, tei.trackedEntity,\
                 tei.orgUnit, insuree.validity_from))
            # add profession attributes
            if insuree.profession_id != None and is_valid_uid(insureeProgram.profession):
                tei.attributes.insert(AttributeValue(insureeProgram.profession,\
                  GeneralConfiguration.get_profession_code(insuree.profession_id))) 
            # add poverty attributes
            if insuree.poverty_id != None and is_valid_uid(insureeProgram.poverty):
                tei.attributes.insert(AttributeValue(insureeProgram.poverty,\
                  GeneralConfiguration.get_boolean_code(insuree.poverty_id))) 
            #  "CHFId" // duplicate
            # "insuranceId":"g54R38QNwEi", # Salted data for privay reason
            if insuree.chfid != None and is_valid_uid(insureeProgram.insuranceId):
                tei.attributes.insert(AttributeValue(insureeProgram.insuranceId,\
                 hashlib.md5(salt + insuree.chfid).hexdigest())) 
            # "insureeId":"e9fOa40sDwR",  # should not use it
            # "familiyId": attribute ,
            if insuree.familiy.uuid != None and is_valid_uid(insureeProgram.familiy):
                tei.attributes.insert(AttributeValue(insureeProgram.familiy, insuree.familiy.uuid)) 
            # "dob"
            if insuree.dob != None and is_valid_uid(insureeProgram.dob):
                tei.attributes.insert(AttributeValue(insureeProgram.dob, insuree.dob)) 
            #"education"
            if insuree.education_id != None and is_valid_uid(insureeProgram.education):
                tei.attributes.insert(AttributeValue(insureeProgram.education,\
                 GeneralConfiguration.get_education_code(insuree.education_id))) 
            # "groupType",
            if insuree.family.family_type_id != None and is_valid_uid(insureeProgram.groupType):
                tei.attributes.insert(AttributeValue(insureeProgram.groupType,\
                 GeneralConfiguration.get_group_type_code(insuree.family.family_type_id))) 
            # "firstName"
            if insuree.other_name != None and is_valid_uid(insureeProgram.firstName):
                tei.attributes.insert(AttributeValue(insureeProgram.firstName, insuree.other_name)) 
            #"firstServicePoint":"GZ6zgXS25VH",
            if insuree.health_facility.uuid != None and is_valid_uid(insureeProgram.firstServicePoint):
                tei.attributes.insert(AttributeValue(insureeProgram.firstServicePoint,\
                 insuree.health_facility.uuid)) 
            #"gender":
            if insuree.gender_id != None and is_valid_uid(insureeProgram.gender):
                tei.attributes.insert(AttributeValue(insureeProgram.gender,\
                 GeneralConfiguration.get_gender_code(insuree.gender_id))) 
            #"isHead":"siOTMqr9kw6",
            if insuree.head != None and is_valid_uid(insureeProgram.isHead):
                tei.attributes.insert(AttributeValue(insureeProgram.isHead,\
                  GeneralConfiguration.get_boolean_code(insuree.head))) 
            #"identificationId":"MFPEijajdy7", # not used for privacy reason
            #if insuree.passport != None and is_valid_uid(insureeProgram.identificationId):
            #    tei.attributes.insert(AttributeValue(insureeProgram.identificationId, insuree.passport)) 
            #"identificationSource":"jOnARr3GARW", # not used for now
            #if insuree.card_issued  != None and is_valid_uid(insureeProgram.identificationSource):
            #    tei.attributes.insert(AttributeValue(insureeProgram.identificationSource,  GeneralConfiguration.get_identification_source_code(insuree.card_issued_id))) 
            #"maritalSatus":"vncvDog0YwP",
            if insuree.marital != None and is_valid_uid(insureeProgram.maritalSatus):
                tei.attributes.insert(AttributeValue(insureeProgram.maritalSatus,\
                 GeneralConfiguration.get_marital_code(insuree.marital))) 
            #"phoneNumber": "r9hJ7SJbVvx", # TBC
            #if insuree.poverty != None and is_valid_uid(insureeProgram.poverty):
            #    tei.attributes.insert(AttributeValue(insureeProgram.poverty, insuree.poverty)) 

            return tei
        else
            return None

 
    @classmethod
    def to_enrolment_objs(cls, insurees):
        bundle = EnrollmentBundle()
        for insuree in insurees:
            bundle.Enrollments.insert(cls.to_enrollment_obj(insuree))
        return bundle

    @classmethod   
    def to_enrolment_obj(cls, insurees):
        uid = cls.build_dhis2_id(insuree.uuid)
        return Enrollment(uid, uid, cls.build_dhis2_id(insuree.family.location.uuid), insuree.validity_from)

    @classmethod
    def to_event_obj(cls, insureepolicy):
        event = Event()
        event.program = insureeProgram.id
        event.orgUnit = cls.build_dhis2_id(insureepolicy.insuree.family.location.uuid)
        event.eventDate = insureepolicy.enrollment_date 
        event.status = "COMPLETED"
        event.dataValue = []
        event.trackedEntityInstance = cls.build_dhis2_id(insureepolicy.insuree.uuid)
        event.programStage = insureeProgram.stage["policy"].id
        stageDE = insureeProgram.stage["policy"].data
        if is_valid_uid(stageDE.policyStage):
            event.dataValue.insert(DataValue(stageDE.policyStage,\
                GeneralConfiguration.get_policy_state_code(insureepolicy.policy.stage)))
        if is_valid_uid(stageDE.policyStatus):
            event.dataValue.insert(DataValue(stageDE.policyStatus,\
                GeneralConfiguration.get_policy_status_code(insureepolicy.policy.status)))
        if is_valid_uid(stageDE.product):
            event.dataValue.insert(DataValue(stageDE.product,\
                insureepolicy.policy.product.code + " - " + insureepolicy.policy.prodcut.code))
        if is_valid_uid(stageDE.PolicyValue):
            event.dataValue.insert(DataValue(stageDE.PolicyValue,insureepolicy.policy.value))
        if is_valid_uid(stageDE.expirityDate):
            event.dataValue.insert(DataValue(stageDE.expirityDate,insureepolicy.policy.expiry_date))
        #event.dataValue.insert(DataValue(stageDE.policyId,cls.build_dhis2_id(insureepolicy.policy.uuid)))


    @classmethod
    def to_event_objs(cls, insureepolicies):
        bundle = EventBundle()
        for insureepolicy in insureepolicies:
            bundle.Enrollments.insert(cls.to_enrollment_obj(insureepolicy))
        return bundle

