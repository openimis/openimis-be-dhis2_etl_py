from xml.etree import ElementTree
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from dhis2_etl.adx_transform.adx_models.adx_data import ADXMapping, ADXMappingGroup

_T = TypeVar('_T')


class AbstractADXFormatter(ABC, Generic[_T]):
    @abstractmethod
    def format_adx(self, adx: ADXMapping) -> _T:
        ...

    def adx_from_format(self, adx: _T) -> ADXMapping:
        raise NotImplemented(F"Creating adx object from format `{_T}` not supported.")


class XMLFormatter(AbstractADXFormatter[ElementTree.Element]):
    def format_adx(self, adx: ADXMapping) -> ElementTree.Element:
        root = ElementTree.Element('adx')
        self._build_xml_gorups(adx, root)
        return root

    def _build_xml_gorups(self, adx: ADXMapping, root: ElementTree.Element):
        for group in adx.groups:
            attributes = self._dataclass_to_xml_attrib(group)
            element = ElementTree.SubElement(root, 'group', attrib=attributes)
            self._build_group_data_values(group, element)

    def _build_group_data_values(self, group: ADXMappingGroup, group_root: ElementTree.SubElement):
        for value in group.data_values:
            base_attributes = self._dataclass_to_xml_attrib(value)
            grouping_details = {k.label_name: k.label_value for k in value.aggregations}
            ElementTree.SubElement(group_root, 'dataValue', {**base_attributes, **grouping_details})

    def _dataclass_to_xml_attrib(self, element):
        # String values of adx mapping are treated as attributes
        return {
            k: v for k, v in element.__dict__.items() if isinstance(v, str)
        }
