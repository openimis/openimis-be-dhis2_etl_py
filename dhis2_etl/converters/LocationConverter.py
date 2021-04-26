from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from ..models.dhis2Metadata import *
from ..models.dhis2Dataset import *
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2.utils import *
import hashlib 
from ..utils import toDateStr, toDatetimeStr,build_dhis2_id
import re
import datetime
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
locationConfig = GeneralConfiguration.get_location()
populationDataset = GeneralConfiguration.get_population_dataset()

class LocationConverter(BaseDHIS2Converter):

    @classmethod
    def to_org_unit_objs(cls, objs,  **kwargs):
        organisationUnits = []
        #exclPaternName = '[Ff]unding.*'
        for location in objs:
            #if not re.match(exclPaternName, location.name):
            organisationUnits.append(cls.to_org_unit_obj(location))
        return OrganisationUnitBundle(organisationUnits = organisationUnits)
 
    @classmethod
    def to_org_unit_obj(cls, location,  **kwargs):
        if hasattr(location,'parent') and location.parent != None: # for imis location
            parentId = build_dhis2_id(location.parent.uuid)
        elif hasattr(location,'location') and location.location != None: # for HF
            parentId = build_dhis2_id(location.location.uuid)
        else:
            parentId = locationConfig['rootOrgUnit']    
        if location.validity_to is None:
            closedDate = None
        else:
            closedDate = toDateStr(location.validity_to)
        attributes = [] # TO DO ? not attributes found on DHIS2

        return OrganisationUnit( name = location.code + ' - ' + location.name, shortName = location.code, code = location.uuid,\
            openingDate = '2000-01-01', id = build_dhis2_id(location.uuid), closedDate = closedDate,\
                parent = DHIS2Ref(id = parentId), attributes = attributes)


    @classmethod
    def to_org_unit_group_obj(cls, locations, group_name, id, **kwargs):
        # **kwargs --> group_name
        organisationUnits = []
        # exclPaternName = '[Ff]unding.*'
        if locations is not None:
            for location in locations:
                #if not re.match(exclPaternName, location.name):
                organisationUnits.append(DHIS2Ref(id = build_dhis2_id(location.uuid) ))
            return OrganisationUnitGroupBundle(organisationUnitGroups = [OrganisationUnitGroup(name = group_name, id=id, organisationUnits = organisationUnits)])#  DeltaDHIS2Ref( additions = organisationUnits ))])
        else:
            return OrganisationUnitGroupBundle(organisationUnitGroups = [OrganisationUnitGroup(name = group_name, id=id)])
    @classmethod
    def to_population_datasets(cls, villages, data_set_period, **kwargs):
        dataValues = []
        if villages is not None:
            for village in villages:
                #if not re.match(exclPaternName, location.name):
                villageDataValues = cls.to_population_dataset(village,data_set_period)
                if villageDataValues is not None and villageDataValues.dataValues is not None and len(villageDataValues.dataValues)>0:
                    dataValues += villageDataValues.dataValues
            return DataValueBundle(dataValues = dataValues)
        else:
            null
    @classmethod
    def to_population_dataset(cls, village, data_set_period, **kwargs):
        dataElementValues = []
        

        if village.male_population is not None and\
             village.male_population >0 and populationDataset.get('dataElements').get('malePopulation') is not None:
            DataElement = populationDataset.get('dataElements').get('malePopulation').split('.')
            DataElementID = DataElement[0]
            DataElementCOC = None
            if len(DataElement) > 1:
                DataElementCOC = DataElement[1]    
            dataElementValues.append(DataElementValue(period = data_set_period,\
                 dataElement = DataElementID,\
                 categoryOptionCombo = DataElementCOC,\
                 orgUnit = build_dhis2_id(village.uuid),\
                 value = village.male_population))
        if village.female_population is not None and\
            village.female_population >0 and populationDataset.get('dataElements').get('femalePopulation') is not None:
            DataElement = populationDataset.get('dataElements').get('femalePopulation').split('.')
            DataElementID = DataElement[0]
            DataElementCOC = None
            if len(DataElement) > 1:
                DataElementCOC = DataElement[1]    
            dataElementValues.append(DataElementValue(period = data_set_period,\
                 dataElement = DataElementID,\
                 categoryOptionCombo = DataElementCOC,\
                 orgUnit = build_dhis2_id(village.uuid),\
                 value = village.female_population))
        if village.other_population is not None and\
            village.other_population  >0 and populationDataset.get('dataElements').get('otherPopulation') is not None:
            DataElement = populationDataset.get('dataElements').get('otherPopulation').split('.')
            DataElementID = DataElement[0]
            DataElementCOC = None
            if len(DataElement) > 1:
                DataElementCOC = DataElement[1]    
            dataElementValues.append(DataElementValue(period = data_set_period,\
                 dataElement = DataElementID,\
                 categoryOptionCombo = DataElementCOC,\
                 orgUnit = build_dhis2_id(village.uuid),\
                 value = village.other_population))
        if village.families is not None and\
             village.families >0 and is_valid_uid(populationDataset.get('dataElements').get('familyPopulation')):
            dataElementValues.append(DataElementValue(period = data_set_period,\
                 value = village.male_population,\
                 dataElement = populationDataset.get('dataElements').get('familyPopulation'),
                 orgUnit = build_dhis2_id(village.uuid)))
        # in case no cat are configured
        if (village.male_population is not None or village.female_population is not None or village.other_population is not None ) and\
             is_valid_uid(populationDataset.get('dataElements').get('population')):
            value = 0
            if village.male_population is not None:
                value += village.male_population
            if village.female_population is not None:
                value += village.female_population
            if village.other_population is not None:
                value += village.other_population
            dataElementValues.append(DataElementValue(period = data_set_period,\
                 value = value,\
                 dataElement = populationDataset.get('dataElements').get('population'),
                 orgUnit = build_dhis2_id(village.uuid)))
        return DataValueBundle( dataValues = dataElementValues)
