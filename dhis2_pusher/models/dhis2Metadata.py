# DHIS2 metadata
# Copyright Patrick Delcoix <patrick@pmpd.eu>

from typing import Dict, List, Optional, Union, Tuple
from enum import Enum, IntEnum
from datetime import datetime, date
from uuid import uuid4
from pydantic import constr, BaseModel, ValidationError, validator, Field, AnyUrl, EmailStr
from dhis2.utils import *
from .dhis2Enum import FeatureType, ValueType
from .dhis2Type import uid, dateStr, datetimeStr, DHIS2Ref, DeltaDHIS2Ref, str50, str150, str230, str130, str255




class OrganisationUnit(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: str50
    name: str230 # max 230
    shortName: str50 # max 50
    description: Optional[str] # TBC
    openingDate: dateStr
    closedDate: Optional[dateStr]
    comment : Optional[str] # TBC
    featureType: Optional[FeatureType]  # NONE | MULTI_POLYGON | POLYGON | POINT | SYMBOL 
    coordinates: Optional[Tuple[float, float]]
    url: Optional[AnyUrl]
    contactPerson: Optional[str]
    address: Optional[str]
    email: Optional[EmailStr] # max 150
    phoneNumber: Optional[str150] # max 150
    parent: Optional[DHIS2Ref]




class OrganisationUnitGroup(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: Optional[str]
    name: str230
    shortName: Optional[str]
    description: Optional[str]
    organisationUnits:Union[List[DHIS2Ref],DeltaDHIS2Ref] = []
    # color
    # symbol

class OrganisationUnitGroupSet(BaseModel):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    id: Optional[uid]
    code: Optional[str50]
    name: Optional[str230]
    description: Optional[str] # TBC
    organisationUnitGroups:Union[List[DHIS2Ref],DeltaDHIS2Ref] = []
    # datadimention
    # compulsory
    # include sub hiearchy

class OrganisationUnitGroupSetBundle(BaseModel):
    organisationUnitGroupSets:List[OrganisationUnitGroupSet]

class OrganisationUnitGroupBundle(BaseModel):
    organisationUnitGroups:List[OrganisationUnitGroup]

class OrganisationUnitBundle(BaseModel):
    organisationUnits:List[OrganisationUnit]

# OptionSet and options

class OptionSet(BaseModel):
    id: Optional[uid]
    name: str230
    code: Optional[str50]
    valueType: ValueType
    options: List[DHIS2Ref]

class Option(BaseModel):
    id: Optional[uid]
    code: str50
    name: Union[float, int, dateStr, datetimeStr, str, DHIS2Ref, bool]
    # type, maybe other class of option are required
class OptionNumber(Option):
    name: float

class OptionInteger(Option):
    name: int

class OptionDate(Option):
    name: dateStr

class OptionDateTime(Option):
    name: datetimeStr

class OptionEmail(Option):
    name: EmailStr

class OptionText(Option):
    name: str130 # TBC

class OptionUid(Option): # for TEI, orgunit
    name: DHIS2Ref # TBC

class OptionBool(Option): # for YesNo YesOnly
    name: bool # TBC if not Emun

class OptionSetBundle(BaseModel):
    optionSets: List[OptionSet]

class OptionBundle(BaseModel):
    options: List[Option]