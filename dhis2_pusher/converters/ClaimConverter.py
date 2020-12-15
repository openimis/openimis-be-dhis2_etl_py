from claim.models import Claim, ClaimItem, ClaimService
from medical.models import Diagnosis, Item, Service
from insuree.models import InsureePolicy
from policy.models import Policy
from product.models import ProductItem, ProductService
from . import models

class ClaimConverter(BaseDHIS2Converter):

    @classmethod
    def to_tei_obj(cls, obj):
        raise NotImplementedError('`to_tei_obj()` must be implemented.')  # pragma: no cover
 
    @classmethod
    def to_enrolment_obj(cls, obj):
        raise NotImplementedError('`to_enrolment_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_event_obj(cls, obj):
        raise NotImplementedError('`to_event_obj()` must be implemented.')  # pragma: no cover