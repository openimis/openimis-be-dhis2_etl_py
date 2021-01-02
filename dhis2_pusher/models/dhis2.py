# FROM https://github.com/dhis2/dhis2-python/blob/main/dhis2_core/src/dhis2/e2b/models/e2b.py
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from dhis2 import utils
#FIXME add dataset model

# Create your models here.



class TrackedEntityInstanceBundle(BaseModel):
    trackedEntityInstances:List[trackedEntityInstance]

class EventBundle(BaseModel):
    events:List[Event]

class EnrollmentBundle(BaseModel):
    enrolments:List[Enrolment]

class EventDataValue(BaseModel):
    created: datetime
    lastUpdated: datetime
    dataElement: str
    value: str
    providedElsewhere: bool
    storedBy: Optional[str]
    @validator('dataElement')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()
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
    @validator('event')
    @validator('program')
    @validator('programStage')
    @validator('orgUnit')
    @validator('trackedEntityInstance')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()

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
    @validator('enrollment')
    @validator('orgUnit')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()
    def __init__(self, id, tei, orgunit, completedDate):
        self.enrollment = id
        self.trackedEntityInstance = tei
        self.completedDate = completedDate
        self.status = "COMPLETED"
        self.orgUnit = orgunit


class AttributeValue(BaseModel):
    created: datetime
    lastUpdated: datetime
    attribute: str
    value: str
    storedBy: Optional[str]
    @validator('attribute')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()
    
    def __init__(self, id, value):
        self.attribute = id
        self.value = value


class trackedEntityInstance(BaseModel):
    created: datetime
    lastUpdated: datetime
    trackedEntity: str
    trackedEntityType: str
    orgUnit: str
    storedBy: Optional[str]
    enrollments: List[Enrollment] = []
    attributes: Union[Dict[str, AttributeValue], List[AttributeValue]] = []
    @validator('trackedEntity')
    @validator('orgUnit')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()

class organisationUnit(BaseModel)
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
    coordinates: tuple[float,float]
    url: AnyUrl
    contactperson: str
    address: str
    email: EmailStr
    phonenumber: str
    parent: str
    @validator('url')
    @validator('address')
    @validator('contactperson')
    def code_length_255(cls, code):
        if len(code) > 50
            raise ValidationError()
    @validator('code')
    @validator('shortname')
    def code_length_50(cls, code):
        if len(code) > 50
            raise ValidationError()
    @validator('id')
    @validator('parent')
    def must_be_valid_uid(cls, uid):
        if not is_valid_uid(uid):
            raise ValidationError()