from insuree.models import Insuree, Gender, Education, Profession, Family
from location.models import Location
from product.models import Product
from . import models

class InsureeConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_obj(cls, obj):
        raise NotImplementedError('`to_tei_obj()` must be implemented.')  # pragma: no cover
 
    @classmethod
    def to_enrolment_obj(cls, obj):
        raise NotImplementedError('`to_enrolment_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_event_obj(cls, obj):
        raise NotImplementedError('`to_event_obj()` must be implemented.')  # pragma: no cover