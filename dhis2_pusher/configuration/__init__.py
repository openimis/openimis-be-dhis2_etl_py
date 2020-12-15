
import sys

class BaseConfiguration(object):  # pragma: no cover

    @classmethod
    def build_configuration(cls, cfg):
        raise NotImplementedError('`build_configuration()` must be implemented.')

    @classmethod
    def get_config(cls):
        module_name = "api_fhir_r4"
        return sys.modules[module_name]