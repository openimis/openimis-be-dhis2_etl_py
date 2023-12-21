import json

from . import BaseConfiguration


class GeneralConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        config = cls.get_config()
        config.dhis2 = cfg['dhis2']
        config.adx = cfg['adx']
        config.salt = cfg['salt']
        config.insureeProgram = cfg['insureeProgram']
        config.claimProgram = cfg['claimProgram']
        config.fundingProgram = cfg['fundingProgram']
        config.populationDataset = cfg['populationDataset']
        config.optionSet = cfg['optionSet']
        # config.genderCodes = cfg['genderCodes']
        # config.educationCodes = cfg['educationCodes']
        # config.professionCodes = cfg['professionCodes']
        config.visitTypeCodes = cfg['visitTypeCodes']
        config.maritalStatusCodes = cfg['maritalStatusCodes']
        config.booleanCodes = cfg['booleanCodes']
        # config.groupTypeCodes = cfg['groupTypeCodes']
        config.default_page_size = cfg['default_page_size']
        config.policyStageCode = cfg['policyStateCode']
        config.policyStatusCode = cfg['policyStatusCode']
        config.claimStatusCode = cfg['claimStatusCode']
        config.location = cfg['location']
        config.jsonOutPath = cfg['jsonOutPath']
        config.scheduled_integration = cfg['scheduled_integration']


    @classmethod
    def get_dhis2(cls):
        return cls.get_config().dhis2

    @classmethod
    def get_adx(cls):
        return cls.get_config().adx

    @classmethod
    def get_insuree_program(cls):
        return cls.get_config().insureeProgram

    @classmethod
    def get_salt(cls):
        return cls.get_config().salt

    @classmethod
    def get_policy_state_code(cls, code):
        return cls.get_config().policyStageCode.get(str(code), 'New Policy')

    @classmethod
    def get_policy_status_code(cls, code):
        return cls.get_config().policyStatusCode.get(str(int(code)), 'Idle')

    @classmethod 
    def get_claim_status_code(cls, code):
        return cls.get_config().claimStatusCode.get(str(int(code)), 'Valuated')

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
        return cls.get_config().booleanCodes.get(str(int(code)), 'No')

    @classmethod
    def get_marital_status_code(cls, code):
        return cls.get_config().maritalStatusCodes.get(str(code), 'Single')

    @classmethod
    def get_visit_type_code(cls, code):
        return cls.get_config().visitTypeCodes.get(str(code), 'Other')


    # @classmethod
    # def get_group_type_code(cls, code):
    #     return cls.get_config().groupTypeCodes.get(code, 'Other')


    @classmethod
    def get_default_page_size(cls):
        return cls.get_config().default_page_size

    @classmethod
    def show_system(cls):
        return 0