import re
from abc import ABC


class BaseDHIS2Converter(ABC):

    @classmethod
    def to_tei_objs(cls, objs, **kwargs):
        raise NotImplementedError('`to_tei_objs()` must be implemented.')  # pragma: no cover
    @classmethod
    def to_tei_obj(cls, obj, **kwargs):
        raise NotImplementedError('`to_tei_obj()` must be implemented.')  # pragma: no cover
 
    @classmethod
    def to_enrollment_obj(cls, obj, **kwargs):
        raise NotImplementedError('`to_enrollment_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_enrollment_objs(cls, objs, **kwargs):
        raise NotImplementedError('`to_enrollment_objs()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_event_obj(cls, obj, **kwargs):
        raise NotImplementedError('`to_event_obj()` must be implemented.')  # pragma: no cover
    @classmethod
    def to_event_objs(cls, obj, **kwargs):
        raise NotImplementedError('`to_event_objs()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_data_element_obj(cls, de_id, obj, **kwargs):
        raise NotImplementedError('`to_data_element_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_data_set_obj(cls, de_id, obj, **kwargs):
        raise NotImplementedError('`to_data_set_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_org_unit_objs(cls, objs, **kwargs):
        raise NotImplementedError('`to_org_unit_objs()` must be implemented.')
    @classmethod
    def to_org_unit_obj(cls, objs, **kwargs):
        raise NotImplementedError('`to_org_unit_obj()` must be implemented.')


