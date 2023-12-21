import hashlib
# import the logging library
import logging

from dhis2.utils import *

from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.utils import build_dhis2_id, toDateStr

from . import BaseDHIS2Converter
from .ClaimConverter import ClaimConverter

# Get an instance of a logger
logger = logging.getLogger('openIMIS')
# Create your views here.
insureeProgram = GeneralConfiguration.get_insuree_program()
salt = GeneralConfiguration.get_salt()

class InsureeConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_objs(cls, objs,  event = False, claim = False, **kwargs):
        #event  = kwargs.get('event',False)
        trackedEntityInstances = []
        for insuree in objs:
            trackedEntityInstances.append(cls.to_tei_obj(insuree, event = event, claim = claim))
        return TrackedEntityInstanceBundle(trackedEntityInstances = trackedEntityInstances)

    @classmethod
    def to_tei_obj(cls, insuree,  event = False, claim = False, **kwargs):
        #event  = kwargs.get('event',False)
        if insuree is not None and insuree.uuid is not None  and insuree.family is not None and insuree.family.uuid is not None:
            attributes = []
            # add insureeId
            if insuree.uuid is not None and is_valid_uid(insureeProgram.get('attributes').get('insureeId')):
                attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('insuranceId'),\
                    value =  insuree.uuid))
            # CHIF ID
            if insuree.chf_id is not None and is_valid_uid(insureeProgram.get('attributes').get('CHFId')):
                attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('CHFId'),\
                    value =  hashlib.md5((salt + insuree.chf_id).encode('utf-8') ).hexdigest()))

            # "familyId": attribute ,
            if insuree.family.uuid is not None and is_valid_uid(insureeProgram.get('attributes').get('familyId')):
                attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('familyId'),\
                    value =  insuree.family.uuid)) 
            # "firstName"
            if insuree.other_names is not None and is_valid_uid(insureeProgram.get('attributes').get('firstName')):
                attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('firstName'),\
                    value = insuree.other_names )) 
            # "lastName"
            if insuree.last_name is not None and is_valid_uid(insureeProgram.get('attributes').get('lastName')):
                attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('lastName'),\
                    value = insuree.last_name )) 
            orgUnit = build_dhis2_id(insuree.family.location.uuid)
            trackedEntity = build_dhis2_id(insuree.uuid)
            enrollments = []
            enrollments.append(cls.to_enrollment_obj(insuree, event=event))
            if claim is True:
                for claim in insuree.claim_set.all():
                    enrollments.append(ClaimConverter.to_enrollment_obj(claim, event = event))
            return TrackedEntityInstance(\
                trackedEntityType = insureeProgram['teiType'],\
                trackedEntityInstance = trackedEntity,\
                orgUnit = orgUnit,\
                enrollments= enrollments,\
                attributes = attributes)
             
        else:
            return None

 
    @classmethod
    def to_enrollment_objs(cls, insurees,  event = False , **kwargs):
        #event  = kwargs.get('event',False)
        Enrollments = []
        for insuree in insurees:
            Enrollments.append(cls.to_enrollment_obj(insuree, event=event))
        return EnrollmentBundle(enrollments = Enrollments)

    @classmethod   
    def to_enrollment_obj(cls, insuree, event = False, **kwargs):
        uid = build_dhis2_id(insuree.uuid)
        #event  = kwargs.get('event',False)
        attributes = []
        if insuree.last_name is not None and is_valid_uid(insureeProgram.get('attributes').get('lastName')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('lastName'),\
                value = insuree.last_name )) 
        # add profession attributes
        if insuree.profession_id is not None and is_valid_uid(insureeProgram.get('attributes').get('profession')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('profession'),\
                value = insuree.profession_id)) 
        # add poverty attributes
        if insuree.family.poverty is not None and is_valid_uid(insureeProgram.get('attributes').get('poverty')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('poverty'),\
                value = GeneralConfiguration.get_boolean_code(insuree.family.poverty))) 
        
        # "insuranceId":"g54R38QNwEi", # Salted data for privay reason
        if insuree.chf_id is not None and is_valid_uid(insureeProgram.get('attributes').get('insuranceId')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('insuranceId'),\
                value =  hashlib.md5((salt + insuree.chf_id).encode('utf-8') ).hexdigest())) 
        if insuree.chf_id is not None and is_valid_uid(insureeProgram.get('attributes').get('CHFId')):
        #  "CHFId" // duplicate
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('CHFId'),\
                value =  hashlib.md5((salt + insuree.chf_id).encode('utf-8') ).hexdigest()))
        # "insureeId":"e9fOa40sDwR",  # should not use it
        # "familyId": attribute ,
        if insuree.family.uuid is not None and is_valid_uid(insureeProgram.get('attributes').get('familyId')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('familyId'),\
                value =  insuree.family.uuid)) 
        # "dob"
        if insuree.dob is not None and is_valid_uid(insureeProgram.get('attributes').get('dob')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('dob'),\
                value =  toDateStr(insuree.dob))) 
        #"education"
        if insuree.education_id is not None and is_valid_uid(insureeProgram.get('attributes').get('education')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('education'),\
                value =  insuree.education_id)) 
        # "groupType",
        if insuree.family.family_type_id is not None and is_valid_uid(insureeProgram.get('attributes').get('groupType')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('groupType'),\
                value =  insuree.family.family_type_id)) 
        # "firstName"
        if insuree.other_names is not None and is_valid_uid(insureeProgram.get('attributes').get('firstName')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('firstName'),\
                value = insuree.other_names )) 
        #"firstServicePoint":"GZ6zgXS25VH",
        if insuree.health_facility is not None and is_valid_uid(insureeProgram.get('attributes').get('firstServicePoint')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('firstServicePoint'),\
                value =  build_dhis2_id(insuree.health_facility.uuid))) 
        #"gender":
        if insuree.gender_id is not None and is_valid_uid(insureeProgram.get('attributes').get('gender')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('gender'),\
                value = insuree.gender_id)) 
        #"isHead":"siOTMqr9kw6",
        if insuree.head is not None and is_valid_uid(insureeProgram.get('attributes').get('isHead')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('isHead'),\
                value = GeneralConfiguration.get_boolean_code(insuree.head))) 
        #"identificationId":"MFPEijajdy7", # not used for privacy reason
        #if insuree.passport is not None and is_valid_uid(insureeProgram.get('attributes').get('identificationId')):
        #    attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('identificationId'),value = insuree.passport)) 
        #"identificationSource":"jOnARr3GARW", # not used for now
        #if insuree.card_issued is not None and is_valid_uid(insureeProgram.get('attributes').get('identificationSource')):
        #    attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('identificationSource'), value = GeneralConfiguration.get_identification_source_code(insuree.card_issued_id))) 
        #"maritalSatus":"vncvDog0YwP",
        if insuree.marital is not None and is_valid_uid(insureeProgram.get('attributes').get('maritalSatus')):
            attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('maritalSatus'),\
                value = GeneralConfiguration.get_marital_status_code(insuree.marital)))
        #"phoneNumber": "r9hJ7SJbVvx", # TBC
        #if insuree.poverty is not None and is_valid_uid(insureeProgram.get('attributes').get('poverty')):
        #attributes.append(AttributeValue(attribute = insureeProgram.get('attributes').get('poverty'), value = insuree.poverty)) 
        events = []
        if event:
            for insureepolicy in insuree.insuree_policies.all():
                events.append(cls.to_event_obj(insureepolicy, insuree = insuree))
        return Enrollment( enrollment = uid, trackedEntityInstance = uid, incidentDate = toDateStr(insuree.validity_from), enrollmentDate = toDateStr(insuree.validity_from),\
              orgUnit = build_dhis2_id(insuree.family.location.uuid), status = "ACTIVE", program = insureeProgram['id'],\
                  events = events, attributes = attributes )
        

    @classmethod
    def to_event_obj(cls, insureepolicy, insuree = None, **kwargs):
        #insuree  = kwargs.get('insuree',False)
        stageDE = insureeProgram.get('stages').get('policy').get('dataElements')
        dataValues = []
        if is_valid_uid(stageDE.get('policyStage')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('policyStage'),\
                value = GeneralConfiguration.get_policy_state_code(insureepolicy.policy.stage)))
        if is_valid_uid(stageDE.get('policyStatus')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('policyStatus'),\
                value = GeneralConfiguration.get_policy_status_code(insureepolicy.policy.status)))
        if is_valid_uid(stageDE.get('product')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('product'),\
                value = insureepolicy.policy.product_id))
        if is_valid_uid(stageDE.get('PolicyValue')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('PolicyValue'), value = insureepolicy.policy.value if insureepolicy.policy.value != None else 0))
        if is_valid_uid(stageDE.get('expiryDate')) and insureepolicy.expiry_date is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('expiryDate'), value = toDateStr(insureepolicy.expiry_date )))
        if is_valid_uid(stageDE.get('startDate')) and insureepolicy.start_date is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('startDate'), value = toDateStr(insureepolicy.start_date   )))
        if is_valid_uid(stageDE.get('effectiveDate')) and insureepolicy.effective_date is not None :
            dataValues.append(EventDataValue(dataElement = stageDE.get('effectiveDate'), value = toDateStr(insureepolicy.effective_date)))
        #event.dataValues.append(EventDataValue(dataElement = stageDE.get('policyId'),build_dhis2_id(insureepolicy.policy.uuid)))
        if  insuree is None:
            return Event(\
            event = build_dhis2_id(insureepolicy.id, 'insureePolicy'),\
            program = insureeProgram['id'],\
            orgUnit = build_dhis2_id(insureepolicy.insuree.family.location.uuid),\
            eventDate = toDateStr(insureepolicy.enrollment_date), \
            status = "COMPLETED",\
            dataValues = dataValues,\
            trackedEntityInstance = build_dhis2_id(insureepolicy.insuree.uuid),\
            programStage = insureeProgram.get('stages').get('policy').get('id'))
        else:
            return Event(\
            event = build_dhis2_id(insureepolicy.id, 'insureePolicy'),\
            program = insureeProgram['id'],\
            orgUnit = build_dhis2_id(insuree.family.location.uuid),\
            eventDate = toDateStr(insureepolicy.enrollment_date), \
            status = "COMPLETED",\
            dataValues = dataValues,\
            trackedEntityInstance = build_dhis2_id(insuree.uuid),\
            programStage = insureeProgram.get('stages').get('policy').get('id'))

        


    @classmethod
    def to_event_objs(cls, insureepolicies, **kwargs):
        events = [] 
        for insureepolicy in insureepolicies:
            events.append(cls.to_event_obj(insureepolicy))
        return EventBundle(events = events)

