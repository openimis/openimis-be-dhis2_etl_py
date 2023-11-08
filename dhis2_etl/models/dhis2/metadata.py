# DHIS2 metadata
# Copyright Patrick Delcoix <patrick@pmpd.eu>

from datetime import date, datetime
from enum import  Enum, IntEnum
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4

from dhis2.utils import *
from pydantic import (AnyUrl, BaseModel, EmailStr, Field, ValidationError,
                      constr, validator)

from .enum import *
from .type import (DeltaDHIS2Ref, DHIS2Ref, dateStr, datetimeStr, str50,
                   str130, str150, str230, str255, uid)

DEFAULT_CATEGORY_COMBO  = DHIS2Ref(id = "bjDvmb4bfuf" )
DEFAULT_CATEGORY_OPTION  = DHIS2Ref(id = "xYerKDKCefk" )
DEFAULT_CATEGORY  = DHIS2Ref(id = "xYerKDKCefk" )
DEFAULT_CATEGORY_OPTION_COMBO  = DHIS2Ref(id = "HllvX50cXC0" )

INDICATOR_PERCENT = DHIS2Ref(id = "hmSnCXmLYwt" )
INDICATOR_UNIT = DHIS2Ref(id = "kHy61PbChXr")

class Metadata(BaseModel):
    name: str230
    id: Optional[uid]
    code: Optional[str50]
    shortName: Optional[str50]

class MetadataSn(Metadata):
    shortName: str50 = ''

class OrganisationUnit(MetadataSn):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
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




class OrganisationUnitGroup(MetadataSn):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    description: Optional[str]
    organisationUnits:Union[List[DHIS2Ref],DeltaDHIS2Ref] = []
    # color
    # symbol

class OrganisationUnitGroupSet(MetadataSn):
    created: Optional[datetimeStr]
    lastUpdated: Optional[datetimeStr]
    description: Optional[str] # TBC
    organisationUnitGroups:Union[List[DHIS2Ref],DeltaDHIS2Ref] = []
    # datadimention
    # compulsory
    # include sub hiearchy

# OptionSet and options

class OptionSet(Metadata):
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

    

class Category(MetadataSn):
    dataDimensionType: DataDimensionType
    categoryOptions: List[DHIS2Ref]

    

 
class CategoryCombo(Metadata):
    categories : List[DHIS2Ref]
    dataDimensionType: DataDimensionType 
    
class AttributeValues(Metadata):
    optionSet: Optional[OptionSet]


 
class CategoryOption(MetadataSn):
    pass
 

class BaseName(BaseModel):
    description: Optional[str230]
    displayDescription: Optional[str230]
    displayShortName: Optional[str50]


class DataElement(MetadataSn,BaseName):
    aggregationType : AggregationType 
    domainType: DomainType
    valueType: ValueType
    categoryCombo : Optional[DHIS2Ref] = DEFAULT_CATEGORY_COMBO
    optionSet: Optional[DHIS2Ref]
    formName: Optional[str50]
    zeroIsSignificant: bool = False
    #translations = List[Translations] = []
    #attributeValues = List[AttributeValues] = []
    #legendSets: List[LegendSet] = []
    #aggregationLevels: List[AggregationLevels] = []

class DataSetElement(BaseModel):
    dataElement : DHIS2Ref
    dataSet : DHIS2Ref

class DataSet(MetadataSn):
    dataSetElements: List[DataSetElement]
    validCompleteOnly: bool = True
    dataElementDecoration:bool = False
    notifyCompletingUser:bool = False
    noValueRequiresComment:bool = False
    skipOffline:bool = False
    compulsoryFieldsCompleteOnly:bool = False
    fieldCombinationRequired:bool = False
    renderHorizontally:bool = False
    renderAsTabs:bool = False
    mobile:bool = False
    version : int =1
    timelyDays: int = 15
    periodType : PeriodType
    openFuturePeriods: int = 1
    openFuturePeriods: int = 0
    categoryCombo : DHIS2Ref = DEFAULT_CATEGORY_COMBO
    organisationUnits:List[OrganisationUnit] = []
    #attributeValues = List[AttributeValues] = []
    #legendSets: List[LegendSet] = []
    #translations = List[Translations] = []
    #dataInputPeriods = List[DataInputPeriods] = []
    #indicators: List[Indicator] = []
    optionSets: List[OptionSet] = []
class MetadataBundle(BaseModel):
    
    organisationUnits:List[OrganisationUnit] = []
    organisationUnitGroups:List[OrganisationUnitGroup] = []
    organisationUnitGroupSets:List[OrganisationUnitGroupSet] = []
    categories: List[Category] = []
    options: List[Option] = []
    optionSets: List[OptionSet] = []
    categoryOptions: List[CategoryOption] = []
    categoryCombos: List[CategoryCombo] = []
    dataElements:List[DataElement]=[]
    dataSets:List[DataSet] =[]
    #indicators: List[Indicator] = []
    #legendSets: List[LegendSet] = []
    #attributeValues = List[AttributeValues] = []