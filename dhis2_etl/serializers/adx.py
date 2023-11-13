from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from xml.etree import ElementTree

from dhis2_etl.models.adx.data import ADXMapping, ADXMappingGroup
from dhis2_etl.utils import clean_code
_T = TypeVar('_T')


class AbstractADXFormatter(ABC, Generic[_T]):
    @abstractmethod
    def format_adx(self, adx: ADXMapping) -> _T:
        ...

    def adx_from_format(self, adx: _T) -> ADXMapping:
        raise NotImplemented(F"Creating adx object from format `{_T}` not supported.")

def remove_namespace(doc, namespace='ns0'):
    """Remove namespace in the passed document in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    if doc.tag.startswith(ns):
        doc.tag = doc.tag[nsl:]
    # Due to api change. getiterator version should be removed after some time
    for elem in doc.iter() if hasattr(doc, 'iter') else doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]

class XMLFormatter(AbstractADXFormatter[ElementTree.Element]):

    
    def format_adx(self, adx: ADXMapping) -> ElementTree.Element:

        xml_root = ElementTree.Element('adx', {'xmlns':"urn:ihe:qrph:adx:2015", 
                                               'xmlns:xsi':"http://www.w3.org/2001/XMLSchema-instance",
                                               'xsi:schemaLocation':"urn:ihe:qrph:adx:2015 ../schema/adx_loose.xsd"})
        # remove ns0
        
        self._build_xml_groups(adx, xml_root)
        if len(list(xml_root))>0:
            remove_namespace(xml_root)
            return xml_root

    def _build_xml_groups(self, adx: ADXMapping, root: ElementTree.Element):
        for group in adx.groups:
            grouping_details = {"ATT_"+clean_code(k.label_name): clean_code(k.label_value) for k in group.aggregations} if group.aggregations else {}
            base_attributes = self._dataclass_to_xml_attrib(group)
            xml_group  = self._build_xml_group(group, {**base_attributes, **grouping_details})
            if xml_group is not None:
                root.append(xml_group)

    def _build_xml_group(self, group: ADXMappingGroup, attributes):
        
        xml_group = ElementTree.Element('group', attrib=att_to_camelcase(attributes))
        for value in group.data_values:
            base_attributes = self._dataclass_to_xml_attrib(value)
            grouping_details = {clean_code(k.label_name): clean_code(k.label_value) for k in value.aggregations}
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
    # don't camel case UPPER
    if word.upper() == word:
        return word
    return word.split('_')[0] + ''.join(x.capitalize() or '_' for x in word.split('_')[1:])

def att_to_camelcase(attributes):
    return {to_camelcase(key) : value for key, value in attributes.items()  }