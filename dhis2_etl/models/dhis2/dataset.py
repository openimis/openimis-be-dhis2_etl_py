# DHIS2 dataset
# Copyright Patrick Delcoix <patrick@pmpd.eu>

from typing import List, Optional

from dhis2.utils import *
from pydantic import BaseModel

from .type import DHIS2Ref, dateStr, datetimeStr, period, uid


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