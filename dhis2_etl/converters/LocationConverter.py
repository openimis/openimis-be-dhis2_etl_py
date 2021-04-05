from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from ..models.dhis2Metadata import *
from . import BaseDHIS2Converter
from ..configurations import GeneralConfiguration
from dhis2.utils import *
import hashlib 
from ..utils import toDateStr, toDatetimeStr,build_dhis2_id
import re
# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
locationConfig = GeneralConfiguration.get_location()


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

