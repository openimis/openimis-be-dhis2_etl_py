from .configurations import BaseConfiguration


class GeneralConfiguration(BaseConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        config = cls.get_config()
        config.dhis2 = cfg['dhis2']
        config.salt = cfg['salt']
        config.insureeProgram = cfg['insureeProgram']
        config.claimProgram = cfg['claimProgram']
        config.genderCodes = cfg['genderCodes']
        config.educationCodes = cfg['educationCodes']
        config.professionCodes = cfg['professionCodes']
        config.maritalStatusCodes = cfg['maritalStatusCodes']
        config.booleanCodes = cfg['booleanCodes']
        config.groupTypeCodes = cfg['groupTypeCodes']
        config.default_page_size = cfg['default_page_size']

    @classmethod
    def get_dhis2(cls):
        return cls.get_config().dhis2
    @classmethod
    def get_gender_code(cls, code):
        return cls.get_config().genderCodes.get(code, 'Unknown')

    @classmethod
    def get_education_code(cls, code):
        return cls.get_config().educationCodes.get(code, 'Other')

    @classmethod
    def get_profession_code(cls, code):
        return cls.get_config().professionCodes.get(code, 'Other')


    @classmethod
    def get_boolean_code(cls, code):
        return cls.get_config().booleanCodes.get(code, 'No')

    @classmethod
    def get_marital_status_code(cls, code):
        return cls.get_config().maritalStatusCodes.get(code, 'Single')

    @classmethod
    def get_group_type_code(cls, code):
        return cls.get_config().groupTypeCodes.get(code, 'Other')


    @classmethod
    def get_default_page_size(cls):
        return cls.get_config().default_page_size

    @classmethod
    def show_system(cls):
        return 0