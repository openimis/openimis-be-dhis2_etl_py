from dhis2.utils import *
from dhis2_etl.configurations import GeneralConfiguration
from dhis2_etl.models.dhis2.program import *
from dhis2_etl.utils import build_dhis2_id, toDateStr

from . import BaseDHIS2Converter

claimProgram =  GeneralConfiguration.get_claim_program()
salt = GeneralConfiguration.get_salt()
CLAIM_REJECTED = 1
CLAIM_ENTERED = 2
CLAIM_CHECKED = 4
CLAIM_PROCESSED = 8
CLAIM_VALUATED = 16

class ClaimConverter(BaseDHIS2Converter):


    @classmethod
    def to_enrollment_obj(cls, claim, event = False , **kwargs):
        if claim is not None and claim.insuree is not None and claim.insuree.uuid is not None:
            trackedEntity = build_dhis2_id(claim.insuree.uuid)
            uid = build_dhis2_id(claim.uuid)
            orgUnit = build_dhis2_id(claim.health_facility.uuid)
            attributes = []
            # claimAdministrator
            if claim.admin is not None and claim.admin.uuid is not None and is_valid_uid(claimProgram.get('attributes').get('claimAdministrator')):
                    attributes.append(AttributeValue(attribute = claimProgram.get('attributes').get('claimAdministrator'),\
                    value = claim.admin.uuid)) 
            #    "claimNumber"
            if claim.code is not None and is_valid_uid(claimProgram.get('attributes').get('claimNumber')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('claimNumber'),\
                    value = claim.code)) 
            #    "diagnoseMain"
            if claim.icd_id is not None and is_valid_uid(claimProgram.get('attributes').get('diagnoseMain')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('diagnoseMain'),\
                    value = claim.icd_id))
            #    "diagnoseSec1"
            if claim.icd_1_id is not None and is_valid_uid(claimProgram.get('attributes').get('diagnoseSec1')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('diagnoseSec1'),\
                    value = claim.icd_1_id))
            #    "diagnoseSec2"
            if claim.icd_2_id is not None and is_valid_uid(claimProgram.get('attributes').get('diagnoseSec2')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('diagnoseSec2'),\
                    value = claim.icd_2_id))
            #    "diagnoseSec3"
            if claim.icd_3_id is not None and is_valid_uid(claimProgram.get('attributes').get('diagnoseSec3')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('diagnoseSec3'),\
                    value = claim.icd_3_id))
            #    "diagnoseSec4"
            if claim.icd_4_id is not None and is_valid_uid(claimProgram.get('attributes').get('diagnoseSec4')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('diagnoseSec4'),\
                    value = claim.icd_4_id))
            #    "VisitType"
            if claim.visit_type is not None and is_valid_uid(claimProgram.get('attributes').get('VisitType')):
                    attributes.append(AttributeValue( attribute = claimProgram.get('attributes').get('VisitType'),\
                    value = GeneralConfiguration.get_visit_type_code(claim.visit_type)))
             # add enroment
            events = []
            if event:
                if claimProgram.get('stages').get('claimDetails') is not None :
                    events.append(cls.to_event_obj(claim)) # add claim details
                if claimProgram.get('stages').get('services') is not None :
                    for service in claim.services.all(): 
                        events.append(cls.to_event_service_obj(service, claim = claim)) # add claim items
                if claimProgram.get('stages').get('items') is not None:
                    for item in claim.items.all():
                        events.append(cls.to_event_item_obj(item, claim = claim)) # add claim service
            return Enrollment(enrollment = uid, trackedEntityInstance = trackedEntity,\
              incidentDate = toDateStr(claim.date_claimed),enrollmentDate = toDateStr(claim.date_claimed),\
              orgUnit = orgUnit, status = "COMPLETED",program = claimProgram['id'],\
                  attributes = attributes,  events = events )
        else:
            return None

 
    @classmethod
    def to_enrollment_objs(cls, claims, event = False, **kwargs):
        Enrollments = []
        for claim in claims:
            Enrollments.append(cls.to_enrollment_obj(claim, event))
        return  EnrollmentBundle(enrollments = Enrollments)

    @classmethod
    def to_event_obj(cls, claim, **kwargs):
        # add claim details event
        stageDE = claimProgram.get('stages').get('claimDetails').get('dataElements')
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = build_dhis2_id(claim.insuree.uuid)
        dataValues = []
        # "status"
        if is_valid_uid(stageDE.get('status')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('status'),\
                value = GeneralConfiguration.get_claim_status_code(claim.status)))
        # "amount"
        if is_valid_uid(stageDE.get('amount')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('amount'), value = claim.claimed ))
        # "checkedDate"
        if is_valid_uid(stageDE.get('checkedDate')):
            dataValues.append(EventDataValue(dataElement = stageDE.get('checkedDate'),\
                 value = toDateStr(claim.date_claimed) ))
        # "processedDate"
        if is_valid_uid(stageDE.get('processedDate')) and claim.process_stamp is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('processedDate'),\
                value = toDateStr(claim.process_stamp)))
        # "adjustedDate"
        if is_valid_uid(stageDE.get('adjustedDate')) and claim.submit_stamp is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('adjustedDate'), \
                value = toDateStr(claim.submit_stamp)))
        if (claim.status == CLAIM_VALUATED or claim.status == CLAIM_PROCESSED):
            # "adjustedAmount"
            if is_valid_uid(stageDE.get('adjustedAmount')) and claim.valuated is not None :
                dataValues.append(EventDataValue(dataElement = stageDE.get('adjustedAmount'),\
                    value = claim.valuated ))
            # "valuationDate" # FIXME not correct in case of batch run
            if is_valid_uid(stageDE.get('valuationDate')):
                if claim.process_stamp is not None:
                    dateEvent = claim.process_stamp.date()
                else:
                    dateEvent = claim.submit_stamp.date()
                dataValues.append(EventDataValue(dataElement = stageDE.get('valuationDate'), \
                    value =  toDateStr(dateEvent)))
            # "approvedAmount":"TiZrzsT8088",
            if is_valid_uid(stageDE.get('approvedAmount')) and claim.approved is not None:
                dataValues.append(EventDataValue(dataElement = stageDE.get('approvedAmount'), \
                    value = claim.approved ))
            # "valuatedAmount":"Fk7sSgbFTaG",
            if is_valid_uid(stageDE.get('valuatedAmount')) and claim.valuated is not None:
                dataValues.append(EventDataValue(dataElement = stageDE.get('valuatedAmount'), \
                    value = claim.valuated))
            # "renumeratedAmount":""
            if is_valid_uid(stageDE.get('renumeratedAmount')) and claim.reinsured is not None:
                dataValues.append(EventDataValue(dataElement = stageDE.get('renumeratedAmount'), \
                    value = claim.reinsured))
        # "rejectionDate"
        elif (claim.status == CLAIM_REJECTED ) and is_valid_uid(stageDE.get('rejectionDate')):
            if claim.process_stamp is not None:
                dateEvent = claim.process_stamp.date()
            else:
                dateEvent = claim.submit_stamp.date()
            dataValues.append(EventDataValue(dataElement = stageDE.get('rejectionDate'),\
                value = toDateStr(dateEvent)))
        return Event(\
            event =  build_dhis2_id(claim.uuid),\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValues = dataValues,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.get('stages').get('claimDetails')['id'])




    @classmethod
    def to_event_item_obj(cls, item, claim = None, **kwargs):
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        trackedEntityInstance = build_dhis2_id(claim.insuree.uuid)
        stageDE = claimProgram.get('stages').get('items').get('dataElements')
        dataValues = []
        #"item":"VFWCqLKPuSd",
        if is_valid_uid(stageDE.get('item')) and item.item_id is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('item'), \
                    value = item.item_id))
        #"quantity":"xBdXypAmk7V", # 
        if is_valid_uid(stageDE.get('quantity')) and item.qty_provided is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('quantity'), \
                    value = item.qty_provided)) 
        #"price":"Gu1DbTMoVGx",
        if is_valid_uid(stageDE.get('price')) and item.price_asked is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('price'), \
                    value = item.price_asked))
        #"deductibleAmount":"uWJD6i5xf6A",
        if is_valid_uid(stageDE.get('deductibleAmount')) and item.deductable_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('deductibleAmount'), \
                    value = item.deductable_amount ))
        #"exeedingCeilingAmount":"krBi9DbQl4Y",
        if is_valid_uid(stageDE.get('exeedingCeilingAmount') ) and item.exceed_ceiling_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('exeedingCeilingAmount') , \
                    value = item.exceed_ceiling_amount ))
        #"renumeratedAmount":"WyAw53dfnMj", # not used
        if is_valid_uid(stageDE.get('renumeratedAmount')) and item.remunerated_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('renumeratedAmount'), \
                    value = item.remunerated_amount ))
        #"seqId":"QmuynKAhycW" # same Service
        #if is_valid_uid(stageDE.get('renumeratedAmount')) and item.reinsured is not None:
        #        dataValues.append(EventDataValue(dataElement = stageDE.get('renumeratedAmount'), \
        #            item.reinsured))     
        return Event(\
            event =  build_dhis2_id(item.id, 'claimItem'),\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValues = dataValues,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.get('stages').get('items')['id'])
           

    @classmethod
    def to_event_service_obj(cls, service, claim = None, **kwargs):
        
        trackedEntityInstance = build_dhis2_id(claim.insuree.uuid)
        orgUnit = build_dhis2_id(claim.health_facility.uuid)
        stageDE = claimProgram.get('stages').get('services').get('dataElements')
        dataValues = []
        #"adjustedAmount"not used
        if is_valid_uid(stageDE.get('adjustedAmount')) and service.price_adjusted is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('adjustedAmount'), \
                    value = service.price_adjusted  ))
        #"approvedAmount" # not used
        if is_valid_uid(stageDE.get('approvedAmount')) and service.price_approved is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('approvedAmount'), \
                    value = service.price_approved  ))
        #"valuatedAmount" # not used
        if is_valid_uid(stageDE.get('valuatedAmount')) and service.remunerated_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('valuatedAmount'), \
                    value = service.remunerated_amount ))
        #"service":
        if is_valid_uid(stageDE.get('service')) and service.service_id is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('service'), \
                    value = service.service_id))
        #"quantity":,
        if is_valid_uid(stageDE.get('quantity')) and service.qty_provided is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('quantity'), \
                    value = service.qty_provided)) 
        #"price":"uwGg814hDhB",
        if is_valid_uid(stageDE.get('price')) and service.price_asked is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('price'), \
                    value = service.price_asked))
        #"deductibleAmount"
        if is_valid_uid(stageDE.get('deductibleAmount')) and service.deductable_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('deductibleAmount'), \
                    value = service.deductable_amount ))
        #"exeedingCeilingAmount"
        if is_valid_uid(stageDE.get('exeedingCeilingAmount') ) and service.exceed_ceiling_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('exeedingCeilingAmount') , \
                    value = service.exceed_ceiling_amount ))
        #"renumeratedAmount": # not used
        if is_valid_uid(stageDE.get('renumeratedAmount')) and service.remunerated_amount is not None:
            dataValues.append(EventDataValue(dataElement = stageDE.get('renumeratedAmount'), \
                    value = service.remunerated_amount ))
        #"seqId":"QmuynKAhycW"
        #if is_valid_uid(stageDE.get('renumeratedAmount')) and service.reinsured is not None:
        #        dataValues.append(EventDataValue(dataElement = stageDE.get('renumeratedAmount'), \
        #            service.reinsured)) 
        return Event(\
            event =  build_dhis2_id(service.id, 'claimService'),\
            program = claimProgram['id'],\
            orgUnit = orgUnit,\
            eventDate = toDateStr(claim.date_from) ,\
            status = "COMPLETED",\
            dataValues = dataValues,\
            trackedEntityInstance = trackedEntityInstance,\
            programStage = claimProgram.get('stages').get('services')['id'])
        
        
    @classmethod
    def to_event_objs(cls, claims, **kwargs):
        events =[]
        for claim in claims:
            if claimProgram.get('stages').get('claimDetails') is not None :
                    events.append(cls.to_event_obj(claim)) # add claim details
            if claimProgram.get('stages').get('services') is not None :
                for service in claim.services.all(): 
                    events.append(cls.to_event_service_obj(service, claim = claim)) # add claim items
            if claimProgram.get('stages').get('items') is not None:
                for item in claim.items.all():
                    events.append(cls.to_event_item_obj(item, claim = claim)) # add claim service

        return EventBundle(events = events)

