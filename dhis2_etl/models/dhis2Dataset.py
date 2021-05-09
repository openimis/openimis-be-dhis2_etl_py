# DHIS2 dataset
# Copyright Patrick Delcoix <patrick@pmpd.eu>

from typing import Dict, List, Optional, Union, Tuple
from enum import Enum, IntEnum
from datetime import datetime, date
from uuid import uuid4
from pydantic import constr, BaseModel, ValidationError, validator, Field, AnyUrl, EmailStr
from dhis2.utils import *
from .dhis2Enum import FeatureType, ValueType
from .dhis2Type import uid, uidList, dateStr, datetimeStr, DHIS2Ref, DeltaDHIS2Ref, str50, str150, str230, str130, str255, period

class DataElementValue(BaseModel):
    dataElement: uid
    period: Optional[period]
    orgUnit: Optional[uid]
    value: Optional[str]
    attributeOptionCombo: Optional[uid] 
    categoryOptionCombo: Optional[uid] 	
    storedBy: Optional[DHIS2Ref]
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    comment: Optional[str] 
    followup: Optional[bool]
    deleted: Optional[bool]

# class to send data to dataset
class DataValueSet(BaseModel):
    dataSet: Optional[uid]
    completeDate: dateStr
    period: period
    orgUnit: uid
    dataValues: List[DataElementValue] = []
    attributeOptionCombo: Optional[uid]
    attributeCategoryOptions : List[uid] = []

class DataValueSetBundle(BaseModel):
    dataValueSets: List[DataValueSet] = []

class DataValueBundle(BaseModel):
    dataValues: List[DataElementValue] = []