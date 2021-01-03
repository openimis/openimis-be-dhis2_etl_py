# FROM https://github.com/dhis2/dhis2-python/blob/main/dhis2_core/src/dhis2/e2b/models/e2b.py
from typing import Dict, List, Optional, Union, Tuple

from pydantic import BaseModel, ValidationError, validator, Field, AnyUrl, EmailStr
from datetime import datetime, date
from uuid import uuid4
from dhis2 import utils
#FIXME add dataset model

# Create your models here.
def must_be_valid_uid(uid):
    if is_valid_uid(uid):
        return uid
    else:
        raise ValidationError()
    
def str_length(str2Test, len):
    if len(str2Test) <= len:
        return str2Test
    else:
        raise ValidationError()

def str_length_255(str2Test):
    return str_length(str2Test, 255)

def str_length_50(str2Test):
    return str_length(str2Test, 50)

class AttributeValue(BaseModel):
    created: datetime
    lastUpdated: datetime
    attribute: str
    value: str
    storedBy: Optional[str]
    # validators
    _uid_check_attribute = validator('attribute', allow_reuse=True)(must_be_valid_uid)
   
    def __init__(self, id, value):
        self.attribute = id
        self.value = value

class EventDataValue(BaseModel):
    created: datetime
    lastUpdated: datetime
    dataElement: str
    value: str
    providedElsewhere: bool
    storedBy: Optional[str]
    #validator 'dataElement'
    _uid_check_dataElement = validator('dataElement', allow_reuse=True)(must_be_valid_uid)

    def __init__(self, de, value):
        self.dataElement = de
        self.value = value

class Event(BaseModel):
    created: datetime
    lastUpdated: datetime
    event: str
    program: str
    programStage: str
    trackedEntityInstance: str
    orgUnit: str
    status: str
    dueDate: datetime
    eventDate: datetime
    completedDate: Optional[str]
    storedBy: Optional[str]
    dataValues: Union[Dict[str, EventDataValue], List[EventDataValue]] = []
    # Validator
    _uid_check_event = validator('event', allow_reuse=True)(must_be_valid_uid)
    _uid_check_program = validator('program', allow_reuse=True)(must_be_valid_uid)
    _uid_check_programStage = validator('programStage', allow_reuse=True)(must_be_valid_uid)
    _uid_check_orgUnit = validator('orgUnit', allow_reuse=True)(must_be_valid_uid)
    _uid_check_trackedEntityInstance = validator('trackedEntityInstance', allow_reuse=True)(must_be_valid_uid)

class Enrollment(BaseModel):
    created: datetime
    lastUpdated: datetime
    enrollment: str
    trackedEntityInstance: str
    orgUnit: str
    storedBy: Optional[str]
    status: str
    completedDate: Optional[str]
    events: List[Event] = []
    attributes: Union[Dict[str, AttributeValue], List[AttributeValue]] = []
    # validator('enrollment','orgUnit')
    _uid_check_enrollment = validator('enrollment', allow_reuse=True)(must_be_valid_uid)
    _uid_check_orgUnit = validator('orgUnit', allow_reuse=True)(must_be_valid_uid)

    def __init__(self, id, tei, orgunit, completedDate):
        self.enrollment = id
        self.trackedEntityInstance = tei
        self.completedDate = completedDate
        self.status = "COMPLETED"
        self.orgUnit = orgunit





class TrackedEntityInstance(BaseModel):
    created: datetime
    lastUpdated: datetime
    trackedEntity: str
    trackedEntityType: str
    orgUnit: str
    storedBy: Optional[str]
    enrollments: List[Enrollment] = []
    attributes: Union[Dict[str, AttributeValue], List[AttributeValue]] = []
    #validator('trackedEntity','orgUnit')
    _uid_check_trackedEntity = validator('trackedEntity', allow_reuse=True)(must_be_valid_uid)
    _uid_check_orgUnit = validator('orgUnit', allow_reuse=True)(must_be_valid_uid)


class organisationUnit(BaseModel):
    created: datetime
    lastUpdated: datetime
    id: str
    code: str
    name: str
    shortname: str
    description: str
    openingdate: date
    closeddate: date
    comment : str
    featuretype: str
    coordinates: Tuple[float, float] 
    url: AnyUrl
    contactperson: str
    address: str
    email: EmailStr
    phonenumber: str
    parent: str
    # validator
    _uid_check_url = validator('url', allow_reuse=True)(str_length_255)
    _uid_check_address = validator('address', allow_reuse=True)(str_length_255)
    _uid_check_contactperson = validator('contactperson', allow_reuse=True)(str_length_255)
    _uid_check_code = validator('code', allow_reuse=True)(str_length_50)
    _uid_check_shortname = validator('shortname', allow_reuse=True)(str_length_50)
    _uid_check_id = validator('id', allow_reuse=True)(must_be_valid_uid)
    _uid_check_parent = validator('parent', allow_reuse=True)(must_be_valid_uid)


    
class TrackedEntityInstanceBundle(BaseModel):
    trackedEntityInstances:List[TrackedEntityInstance]

class EventBundle(BaseModel):
    events:List[Event]

class EnrollmentBundle(BaseModel):
    enrolments:List[Enrollment]