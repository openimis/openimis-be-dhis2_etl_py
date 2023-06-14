from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from xml.etree import ElementTree

from dhis2_etl.models.adx.data import ADXMapping, ADXMappingGroup

_T = TypeVar('_T')


class AbstractADXFormatter(ABC, Generic[_T]):
    @abstractmethod
    def format_adx(self, adx: ADXMapping) -> _T:
        ...

    def adx_from_format(self, adx: _T) -> ADXMapping:
        raise NotImplemented(F"Creating adx object from format `{_T}` not supported.")


class XMLFormatter(AbstractADXFormatter[ElementTree.Element]):
    def format_adx(self, adx: ADXMapping) -> ElementTree.Element:
        xml_root = ElementTree.Element('adx', {'xmlns':"urn:ihe:qrph:adx:2015", 
                                               'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
                                               'xsi:schemaLocation':"urn:ihe:qrph:adx:2015 ../schema/adx_loose.xsd"})
        self._build_xml_groups(adx, xml_root)
        if len(list(xml_root))>0:
            return xml_root

    def _build_xml_groups(self, adx: ADXMapping, root: ElementTree.Element):
        for group in adx.groups:
            xml_group  = self._build_xml_group(group,self._dataclass_to_xml_attrib(group))
            if xml_group is not None:
                root.append(xml_group)

    def _build_xml_group(self, group: ADXMappingGroup, attributes):
        
        xml_group = ElementTree.Element('group', attrib=att_to_camelcase(attributes))
        for value in group.data_values:
            base_attributes = self._dataclass_to_xml_attrib(value)
            grouping_details = {k.label_name: k.label_value for k in value.aggregations}
            if base_attributes is not None:
                ElementTree.SubElement(xml_group, 'dataValue', {**base_attributes, **grouping_details})
        if len(list(xml_group))>0:
            return xml_group

    def _dataclass_to_xml_attrib(self, element):
        # String values of adx mapping are treated as attributes
        if   (not hasattr(element,'value')) or element.value != '0':
            return {
                catch_de(k): v for k, v in element.__dict__.items() if isinstance(v, str) 
            }
def catch_de(s):
    return 'dataElement' if s == 'data_element' else s 
        
def to_camelcase(word):
    return word.split('_')[0] + ''.join(x.capitalize() or '_' for x in word.split('_')[1:])

def att_to_camelcase(attributes):
    return {to_camelcase(key) : value for key, value in attributes.items()  }