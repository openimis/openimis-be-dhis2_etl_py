
import sys


class BaseConfiguration(object):  # pragma: no cover

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_config(cls):
        module_name = "dhis2_etl"
        return sys.modules[module_name]

from .generalConfiguration import GeneralConfiguration
from .moduleConfiguration import ModuleConfiguration
