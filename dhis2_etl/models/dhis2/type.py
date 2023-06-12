# Copyright Patrick Delcoix <patrick@pmpd.eu>
# dhis2 types
from typing import List, Optional

from pydantic import BaseModel, constr

#normal uid
uid = constr(regex="^[a-zA-Z][a-zA-Z0-9]{10}$")
# for Dataelement with Categories
uidList = constr(regex="^[a-zA-Z][a-zA-Z0-9]{10}(.[a-zA-Z][a-zA-Z0-9]{10})*$")
# dates
dateStr = constr(regex="^\d{4}-\d{2}-\d{2}$")
datetimeStr = constr(regex="^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}$")
# string
str50 = constr(regex="^.{0,50}$")
str130 = constr(regex="^.{0,130}$")
str150 = constr(regex="^.{0,150}$")
str230  = constr(regex="^.{0,230}$")
str255  = constr(regex="^.{0,255}$")
period= constr(regex="^(?:[0-9]{4})|(?:[0-9]{6})|(?:[0-9]{8})$")

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


