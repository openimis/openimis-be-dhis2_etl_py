from django.conf import settings

from . import BaseConfiguration
from .generalConfiguration import GeneralConfiguration


class ModuleConfiguration(BaseConfiguration):

    __REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'dhis2.exceptions.dhis2_exception_handler'
    }

    @classmethod
    def build_configuration(cls, cfg):
        GeneralConfiguration.build_configuration(cfg)
 
 

 

