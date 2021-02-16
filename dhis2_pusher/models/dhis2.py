# FROM https://github.com/dhis2/dhis2-python/blob/main/dhis2_core/src/dhis2/e2b/models/e2b.py
from typing import Dict, List, Optional, Union, Tuple

from pydantic import constr, BaseModel, ValidationError, validator, Field, AnyUrl, EmailStr
from datetime import datetime, date
from uuid import uuid4
from dhis2.utils import *
#FIXME add dataset model
uid = constr(regex="^[a-zA-Z][a-zA-Z0-9]{10}$")
dateStr = constr(regex="^\d{4}-\d{2}-\d{2}$")
datetimeStr = constr(regex="^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$")

str50 = constr(regex="^.{0-50}$")
str130 = constr(regex="^.{0-130}$")
str255  = constr(regex="^.{0-255}$")

class DHIS2Ref(BaseModel):
    id: Optional[uid]
    code: Optional[str]

class DeltaDHIS2Ref(BaseModel):
    additions: List[DHIS2Ref] = []
    deletions: List[DHIS2Ref] = []

class AttributeValue(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    attribute: uid
    value: str
    storedBy: Optional[DHIS2Ref]

   

class EventDataValue(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    dataElement: uid
    value: str
    providedElsewhere: Optional[bool]
    storedBy: Optional[DHIS2Ref]



class Event(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    program: uid
    programStage: uid
    trackedEntityInstance: uid
    orgUnit: uid
    status: str
    dueDate: Optional[dateStr]
    eventDate: dateStr
    completedDate: Optional[dateStr]
    storedBy: Optional[DHIS2Ref]
    dataValues: Union[Dict[str, EventDataValue], List[EventDataValue]] = []

class Enrollment(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    trackedEntityInstance: Optional[uid] # optionnal only if part of the TEI creation
    orgUnit: uid
    storedBy: Optional[DHIS2Ref]
    status: str
    incidentDate: dateStr
    enrollmentDate: dateStr
    events: List[Event] = []
    attributes: Union[Dict[str, AttributeValue], List[AttributeValue]] = []
    program: uid



class TrackedEntityInstance(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    trackedEntityType: uid
    orgUnit: uid
    storedBy: Optional[DHIS2Ref]
    enrollments: List[Enrollment] = []
    attributes: Union[Dict[str, AttributeValue], List[AttributeValue]] = []
    #validator('trackedEntity','orgUnit')



class OrganisationUnit(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: str
    name: str # max 230
    shortName: str # max 50
    description: Optional[str]
    openingDate: dateStr
    closedDate: Optional[dateStr]
    comment : Optional[str]
    featureType: Optional[str]  # NONE | MULTI_POLYGON | POLYGON | POINT | SYMBOL 
    coordinates: Optional[Tuple[float, float]]
    url: Optional[AnyUrl]
    contactPerson: Optional[str]
    address: Optional[str]
    email: Optional[EmailStr] # max 150
    phoneNumber: Optional[str] # max 150
    parent: Optional[DHIS2Ref]
    # validator
    #_uid_check_url = validator('url', allow_reuse=True)(str_length_255)
    #_uid_check_address = validator('address', allow_reuse=True)(str_length_255)
    #_uid_check_contactperson = validator('contactperson', allow_reuse=True)(str_length_255)
    #_uid_check_code = validator('code', allow_reuse=True)(str_length_50)
    #_uid_check_shortname = validator('shortname', allow_reuse=True)(str_length_50)



class OrganisationUnitGroup(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: Optional[str]
    name: str
    shortName: Optional[str]
    description: Optional[str]
    organisationUnits:Union[List[DHIS2Ref],DeltaDHIS2Ref]
    # color
    # symbol

class OrganisationUnitGroupSet(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: Optional[str]
    name: Optional[str]
    description: Optional[str]
    organisationUnitGroups:Union[List[DHIS2Ref],DeltaDHIS2Ref]
    # datadimention
    # compulsory
    # include sub hiearchy

class OrganisationUnitGroupSetBundle(BaseModel):
    organisationUnitGroupSets:List[OrganisationUnitGroupSet]

class OrganisationUnitGroupBundle(BaseModel):
    organisationUnitGroups:List[OrganisationUnitGroup]

class OrganisationUnitBundle(BaseModel):
    organisationUnits:List[OrganisationUnit]

class TrackedEntityInstanceBundle(BaseModel):
    trackedEntityInstances:List[TrackedEntityInstance]

class EventBundle(BaseModel):
    events:List[Event]

class EnrollmentBundle(BaseModel):
    enrolments:List[Enrollment]

