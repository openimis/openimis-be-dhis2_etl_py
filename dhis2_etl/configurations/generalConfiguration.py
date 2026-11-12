from django.core.exceptions import ImproperlyConfigured

from . import BaseConfiguration

DHIS2_CONNECTION_KEYS = ("host", "username", "password")


class GeneralConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        config = cls.get_config()
        config.dhis2 = cfg["dhis2"]
        config.adx = cfg["adx"]
        config.salt = cfg.get("salt")
        config.export_names = bool(cfg.get("export_names", False))
        config.insureeProgram = cfg["insureeProgram"]
        config.claimProgram = cfg["claimProgram"]
        config.fundingProgram = cfg["fundingProgram"]
        config.populationDataset = cfg["populationDataset"]
        config.optionSet = cfg["optionSet"]
        # config.genderCodes = cfg['genderCodes']
        # config.educationCodes = cfg['educationCodes']
        # config.professionCodes = cfg['professionCodes']
        config.visitTypeCodes = cfg["visitTypeCodes"]
        config.maritalStatusCodes = cfg["maritalStatusCodes"]
        config.booleanCodes = cfg["booleanCodes"]
        # config.groupTypeCodes = cfg['groupTypeCodes']
        config.default_page_size = cfg["default_page_size"]
        config.policyStageCode = cfg["policyStateCode"]
        config.policyStatusCode = cfg["policyStatusCode"]
        config.claimStatusCode = cfg["claimStatusCode"]
        config.location = cfg["location"]
        config.jsonOutPath = cfg["jsonOutPath"]
        config.scheduled_integration = cfg["scheduled_integration"]

    @classmethod
    def get_dhis2(cls):
        return cls.get_config().dhis2

    @classmethod
    def get_dhis2_connection(cls):
        """
        The DHIS2 host and credentials; raises ImproperlyConfigured when any is
        missing, rather than connecting to an unintended instance.
        """
        dhis2 = cls.get_dhis2() or {}
        missing = [key for key in DHIS2_CONNECTION_KEYS if not dhis2.get(key)]
        if missing:
            raise ImproperlyConfigured(
                "dhis2_etl: the DHIS2 connection is not configured, missing dhis2.%s"
                % ", dhis2.".join(missing)
            )
        return dhis2

    @classmethod
    def missing_settings(cls):
        """The settings a deployment must provide before using the module."""
        dhis2 = cls.get_dhis2() or {}
        missing = ["dhis2.%s" % key for key in DHIS2_CONNECTION_KEYS if not dhis2.get(key)]
        if not cls.get_config().salt:
            missing.append("salt")
        return missing

    @classmethod
    def export_names(cls):
        """Whether the insuree first and last names are exported (off by default)."""
        return bool(getattr(cls.get_config(), "export_names", False))

    @classmethod
    def get_adx(cls):
        return cls.get_config().adx

    @classmethod
    def get_insuree_program(cls):
        return cls.get_config().insureeProgram

    @classmethod
    def get_salt(cls):
        """
        The deployment's secret salt of the pseudonymised identifiers; raises
        ImproperlyConfigured when it is not set, rather than exporting identifiers
        hashed with a salt known to everyone.
        """
        salt = cls.get_config().salt
        if not salt:
            raise ImproperlyConfigured(
                "dhis2_etl: 'salt' is not configured; set a deployment-specific secret salt"
            )
        return salt

    @classmethod
    def get_policy_state_code(cls, code):
        return cls.get_config().policyStageCode.get(str(code), "New Policy")

    @classmethod
    def get_policy_status_code(cls, code):
        return cls.get_config().policyStatusCode.get(str(int(code)), "Idle")

    @classmethod
    def get_claim_status_code(cls, code):
        return cls.get_config().claimStatusCode.get(str(int(code)), "Valuated")

    @classmethod
    def get_claim_program(cls):
        return cls.get_config().claimProgram

    @classmethod
    def get_funding_program(cls):
        return cls.get_config().fundingProgram

    @classmethod
    def get_population_dataset(cls):
        return cls.get_config().populationDataset

    @classmethod
    def get_location(cls):
        return cls.get_config().location

    @classmethod
    def get_json_out_path(cls):
        return cls.get_config().jsonOutPath

    @classmethod
    def get_option_set_uid(cls, name):
        return cls.get_config().optionSet.get(name)

    @classmethod
    def get_scheduled_integration(cls, resource):
        return cls.get_config().scheduled_integration[resource]

    # @classmethod
    # def get_gender_code(cls, code):
    #     return cls.get_config().genderCodes.get(code, 'Unknown')

    # @classmethod
    # def get_education_code(cls, code):
    #     return cls.get_config().educationCodes.get(code, 'Other')

    # @classmethod
    # def get_profession_code(cls, code):
    #     return cls.get_config().professionCodes.get(code, 'Other')

    @classmethod
    def get_boolean_code(cls, code):
        return cls.get_config().booleanCodes.get(str(int(code)), "No")

    @classmethod
    def get_marital_status_code(cls, code):
        return cls.get_config().maritalStatusCodes.get(str(code), "Single")

    @classmethod
    def get_visit_type_code(cls, code):
        return cls.get_config().visitTypeCodes.get(str(code), "Other")

    # @classmethod
    # def get_group_type_code(cls, code):
    #     return cls.get_config().groupTypeCodes.get(code, 'Other')

    @classmethod
    def get_default_page_size(cls):
        return cls.get_config().default_page_size

    @classmethod
    def show_system(cls):
        return 0
