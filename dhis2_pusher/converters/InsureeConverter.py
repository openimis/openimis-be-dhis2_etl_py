from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from ..models.dhis2 import *
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2.utils import *
import hashlib 
from ..utils import toDateStr, toDatetimeStr
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
insureeProgram = GeneralConfiguration.get_insuree_program()
salt = GeneralConfiguration.get_salt()

class InsureeConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs, event = False):
        trackedEntityInstances = []
        for insuree in objs:
            trackedEntityInstances.append(cls.to_tei_obj(insuree, event))
        return TrackedEntityInstanceBundle(trackedEntityInstances = trackedEntityInstances)

    @classmethod
    def to_tei_objs_event(cls, objs):
        return cls.to_tei_objs(objs, True)

    @classmethod
    def to_tei_obj(cls, insuree, event = False):
        if insuree is not None and insuree.uuid is not None  and insuree.family is not None and insuree.family.uuid is not None:
            attributes = []
            # add profession attributes
            if insuree.profession_id is not None and is_valid_uid(insureeProgram['attributes']['profession']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['profession'],\
                    value = GeneralConfiguration.get_profession_code(insuree.profession_id))) 
            # add poverty attributes
            if insuree.family.poverty is not None and is_valid_uid(insureeProgram['attributes']['poverty']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['poverty'],\
                    value =  GeneralConfiguration.get_boolean_code(insuree.family.poverty))) 
            #  "CHFId" // duplicate
            # "insuranceId":"g54R38QNwEi", # Salted data for privay reason
            if insuree.chf_id is not None and is_valid_uid(insureeProgram['attributes']['insuranceId']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['insuranceId'],\
                    value =  hashlib.md5((salt + insuree.chf_id).encode('utf-8') ).hexdigest())) 
            # "insureeId":"e9fOa40sDwR",  # should not use it
            # "familyId": attribute ,
            if insuree.family.uuid is not None and is_valid_uid(insureeProgram['attributes']['familyId']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['familyId'],\
                    value =  insuree.family.uuid)) 
            # "dob"
            if insuree.dob is not None and is_valid_uid(insureeProgram['attributes']['dob']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['dob'],\
                    value =  toDateStr(insuree.dob))) 
            #"education"
            if insuree.education_id is not None and is_valid_uid(insureeProgram['attributes']['education']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['education'],\
                    value =  GeneralConfiguration.get_education_code(insuree.education_id))) 
            # "groupType",
            if insuree.family.family_type_id is not None and is_valid_uid(insureeProgram['attributes']['groupType']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['groupType'],\
                     value =  GeneralConfiguration.get_group_type_code(insuree.family.family_type_id))) 
            # "firstName"
            if insuree.other_names is not None and is_valid_uid(insureeProgram['attributes']['firstName']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['firstName'],\
                    value = insuree.other_names )) 
            #"firstServicePoint":"GZ6zgXS25VH",
            if insuree.health_facility is not None and is_valid_uid(insureeProgram['attributes']['firstServicePoint']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['firstServicePoint'],\
                    value =  insuree.health_facility.uuid)) 
            #"gender":
            if insuree.gender_id is not None and is_valid_uid(insureeProgram['attributes']['gender']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['gender'],\
                    value =GeneralConfiguration.get_gender_code(insuree.gender_id))) 
            #"isHead":"siOTMqr9kw6",
            if insuree.head is not None and is_valid_uid(insureeProgram['attributes']['isHead']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['isHead'],\
                    value =GeneralConfiguration.get_boolean_code(insuree.head))) 
            #"identificationId":"MFPEijajdy7", # not used for privacy reason
            #if insuree.passport is not None and is_valid_uid(insureeProgram['attributes']['identificationId']):
            #    attributes.append(AttributeValue(attribute = insureeProgram['attributes']['identificationId'],value = insuree.passport)) 
            #"identificationSource":"jOnARr3GARW", # not used for now
            #if insuree.card_issued is not None and is_valid_uid(insureeProgram['attributes']['identificationSource']):
            #    attributes.append(AttributeValue(attribute = insureeProgram['attributes']['identificationSource'], value = GeneralConfiguration.get_identification_source_code(insuree.card_issued_id))) 
            #"maritalSatus":"vncvDog0YwP",
            if insuree.marital is not None and is_valid_uid(insureeProgram['attributes']['maritalSatus']):
                attributes.append(AttributeValue(attribute = insureeProgram['attributes']['maritalSatus'],\
                    value =GeneralConfiguration.get_marital_status_code(insuree.marital))) 
            #"phoneNumber": "r9hJ7SJbVvx", # TBC
            #if insuree.poverty is not None and is_valid_uid(insureeProgram['attributes']['poverty']):
            #attributes.append(AttributeValue(attribute = insureeProgram['attributes']['poverty'], value = insuree.poverty)) 
            orgUnit = cls.build_dhis2_id(insuree.family.location.uuid)
            trackedEntity = cls.build_dhis2_id(insuree.uuid)
            events = []
            if event:
                for insureepolicy in insuree.insuree_policies.all():
                    events.append(cls.to_event_obj(insureepolicy,  insuree))
            enrollment = Enrollment(incidentDate = toDateStr(insuree.validity_from), program = insureeProgram['id'],\
                    enrollmentDate = toDateStr(insuree.validity_from), events = events, orgUnit = orgUnit, status = "COMPLETED" )
            return TrackedEntityInstance(\
            trackedEntityType = insureeProgram['teiType'],\
                id = trackedEntity,\
                orgUnit = orgUnit,\
                # add enroment
                enrollments= [enrollment],\
                attributes = attributes)
             
        else:
            return None

 
    @classmethod
    def to_enrolment_objs(cls, insurees):
        Enrollments = []
        for insuree in insurees:
            Enrollments.append(cls.to_enrollment_obj(insuree))
        return EnrollmentBundle(Enrollments)

    @classmethod   
    def to_enrolment_obj(cls, insurees):
        uid = cls.build_dhis2_id(insuree.uuid)
        return Enrollment( trackedEntityInstance = uid, incidentDate = toDateStr(insuree.validity_from), enrollmentDate = toDateStr(insuree.validity_from),\
              orgUnit = cls.build_dhis2_id(insuree.family.location.uuid), status = "COMPLETED", program = insureeProgram['id'] )
        

    @classmethod
    def to_event_obj(cls, insureepolicy, insuree=None):
        stageDE = insureeProgram['stages']["policy"]['dataElements']
        dataValue = []
        if is_valid_uid(stageDE['policyStage']):
            dataValue.append(EventDataValue(dataElement = stageDE['policyStage'],\
                value = GeneralConfiguration.get_policy_state_code(insureepolicy.policy.stage)))
        if is_valid_uid(stageDE['policyStatus']):
            dataValue.append(EventDataValue(dataElement = stageDE['policyStatus'],\
                value = GeneralConfiguration.get_policy_status_code(insureepolicy.policy.status)))
        if is_valid_uid(stageDE['product']):
            dataValue.append(EventDataValue(dataElement = stageDE['product'],\
                value = insureepolicy.policy.product.code + " - " + insureepolicy.policy.product.name))
        if is_valid_uid(stageDE['PolicyValue']):
            dataValue.append(EventDataValue(dataElement = stageDE['PolicyValue'], value = insureepolicy.policy.value))
        if is_valid_uid(stageDE['expirityDate']):
            dataValue.append(EventDataValue(dataElement = stageDE['expirityDate'], value = toDateStr(insureepolicy.policy.expiry_date)))
        #event.dataValue.append(EventDataValue(dataElement = stageDE['policyId'],cls.build_dhis2_id(insureepolicy.policy.uuid)))
        if  insuree is None:
            return Event(\
            program = insureeProgram['id'],\
            orgUnit = cls.build_dhis2_id(insureepolicy.insuree.family.location.uuid),\
            eventDate = toDateStr(insureepolicy.enrollment_date), \
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = cls.build_dhis2_id(insureepolicy.insuree.uuid),\
            programStage = insureeProgram['stages']["policy"]['id'])
        else:
            return Event(\
            program = insureeProgram['id'],\
            orgUnit = cls.build_dhis2_id(insuree.family.location.uuid),\
            eventDate = toDateStr(insureepolicy.enrollment_date), \
            status = "COMPLETED",\
            dataValue = dataValue,\
            trackedEntityInstance = cls.build_dhis2_id(insuree.uuid),\
            programStage = insureeProgram['stages']["policy"]['id'])

        


    @classmethod
    def to_event_objs(cls, insureepolicies):
        events = [] 
        for insureepolicy in insureepolicies:
            events.append(cls.to_event_obj(insureepolicy))
        return EventBundle(events = events)

