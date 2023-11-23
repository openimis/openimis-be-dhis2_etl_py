import logging

from django.apps import AppConfig

from .configurations import ModuleConfiguration

MODULE_NAME = "dhis2_etl"

logger = logging.getLogger('openIMIS')

DEFAULT_CFG = {
    "dhis2" : {
        "host":"https://play.dhis2.org/2.39.3",
        "username":"admin",
        "password":"district"
    },
    "adx": {
        "endpoint": "api/dataValueSets",
        "content_type": "application/adx+xml",
        # https://docs.dhis2.org/en/develop/using-the-api/dhis-core-version-master/data.html#webapi_data_values_import_parameters
        "data_element_id_scheme": "code",
        "org_unit_id_scheme": "code",
        "age_disaggregation":[6, 13, 19, 26, 36, 56, 76],
        "value_disaggregation":[10, 100, 1000, 10000, 100000, 1000000]
    },
    "default":{"category": "GLevLNI9wkl", "categoryCombo":"bjDvmb4bfuf", "categoryOption":"xYerKDKCefk" },
    "salt":"LeSalt",
    "jsonOutPath":'/temp',
    "scheduled_integration": {
        "claims":  False,
        "policies": False,
        "contribution": False,
        "product": False,
        "other_optionset": False,
        "location": False
    },
    "location":{
        "rootOrgUnit":"ImspTQPwCqd",
        "rootOrgUnitName":"DemOpenIMIS",
        "rootOrgUnitCode":"Root",
        "attributes":{
            "locationId":"gMNNTAdZbW1",
            "locationType":"ffZOxd5V2UK"
        }
    },
    "optionSet":{
        "gender": "GUdoValVQSh",
        "profession": "Sd4u2gQx36n",
        "groupType" : "iyfsslkBi1G",
        "education" : "EiSeDNXxNjB",
        "product" : "kCdTMGqxLGE",
        "diagnosis" : "Gg8QVWm9zPh",
        "item": "V2nNlKHYNHE",
        "service": "FxKDNqNDuri"
    }, "visitTypeCodes" : {
        "O" : "Other",
        "R" : "Referal",
        "E" : "Emergency"
    }, "maritalStatusCodes":{
        "M" : "Married",
        "D" : "Divorced",
        "W" : "Widowed",
        "S" : "Single",
        "NF" : "Not specified"# Default 
    },"booleanCodes":{
         "0" : "No", # Default
         "1" : "Yes"
     }, "policyStateCode":{
        "N" : "New Policy",
        "R" : "Renewed Policy"       
    }, "policyStatusCode":{
        "1" : "Idle",
        "2" : "Active",
        "4" : "Suspended",
        "8" : "Expired",
        "16" : "Ready",
        "64" : "Other" # default        
    }, "claimStatusCode":{
        "2" : "Entered",
        "4" : "Checked",
        "1" : "Rejected",
        "8" : "Processed",
        "16" : "Valuated"    
    }, 
    "default_page_size":"250",
    "populationDataset":{
        "id":"bKrBgAUWYK3",
        "dataElements":{
            "malePopulation":"UbpmYBEmuwK.UBIvj1vbywS",
            "femalePopulation":"UbpmYBEmuwK.rcSbWNhTs6X",
            "otherPopulation":"UbpmYBEmuwK.C5CknYRHX9S",
            "familyPopulation":"OYwANZ2NBcZ"
        }
    },
    "insureeProgram" : {
        "id" : "IR5BiEXrBD7",
        "teiType":"EoBGArVCQ69",
        "stages": {
            "policy" : {
                "id":"DVRNDUNwI9s",
                "dataElements": {
                    "policyStage":"j028KRFsjx6", # categoryCombo "bjDvmb4bfuf"
                    "policyStatus":"Q0pEucwW60Z",
                    "product":"NAdBLHAdOGv",
                    "policyId":"NtslGBEMyMy", 
                    "PolicyValue":"mVeMk0sNLZb",
                    "expiryDate":"RzgHQtgsmfB",
                    "startDate":"h2Ck7EyokyI",
                    "effectiveDate":"zrfmkobtJfx"
                    }
            }
        },
        "attributes" : {
            "poverty" : "WeLouCfrfoF",
            "CHFId":"HaVpe5WsCRl", # should not use it
            "insuranceId":"g54R38QNwEi", # Salted data for privay reason
            "insureeId":"e9fOa40sDwR",  # should not use it
            "familyId":"DvT0LSMDW2f",
            "dob":"woZmnhwGvu6",
            "education":"pWV8uthRZVY",
            "groupType":"QnAQO4Kd4I3",
            "firstName":"vYdz8EjQJe0", # not used for privacy reason
            "lastName":"BRGgPOilUtC", # not used for privacy reason
            "firstServicePoint":"GZ6zgXS25VH",
            "gender":"QtkHTKL4EsU",
            "isHead":"siOTMqr9kw6",
            "identificationId":"MFPEijajdy7", # not used for privacy reason
            "identificationSource":"jOnARr3GARW", # not used for now
            "profession":"zy5Br9ZEDLY",
            "maritalSatus":"vncvDog0YwP",
            "phoneNumber": "r9hJ7SJbVvx", # TBC
        }
    }, "claimProgram" : {
        "id" : "vPjOO7Jl6jC",
        "teiType":"EoBGArVCQ69",
        "stages":{
            "claimDetails" : {
                "id" : "J6HPLSiv7Ij",
                "dataElements": {
                    "status":"mGCsTQbv7zA",
                    "amount":"QINoEjSZ9Hs", 
                    "adjustedAmount": "GGZy5cV04QQ",# not used 
                    "checkedDate":"kbPqkHGEuwz",
                    "rejectionDate":"Gm7DjQrYpdH",
                    "processedDate":"QKPo84kaoMm",
                    "valuationDate" : "HbDPuVexDLj",
                    "adjustedDate": "",
                    "approvedAmount":"TiZrzsT8088",
                    "valuatedAmount":"Fk7sSgbFTaG",
                    "renumeratedAmount":""
                    }
            },
            "items" :{
                "id" : "GfHayuoGJLr",
                "dataElements": {
                    "item":"VFWCqLKPuSd",
                    "quantity":"xBdXypAmk7V", #  
                    "price":"Gu1DbTMoVGx",
                    "deductibleAmount":"uWJD6i5xf6A",
                    "exeedingCeilingAmount":"krBi9DbQl4Y",
                    "renumeratedAmount":"WyAw53dfnMj", # not used
                    "seqId":"QmuynKAhycW" # same Service
                    } 
            },
            "services": {
                "id" : "u7wtwsIJ3Dz",
                "dataElements": {
                    "adjustedAmount":"vIkmxPdZpUT",# not used
                    "approvedAmount":"PWX6sv2o9DE",# not used
                    "valuatedAmount":"EkThw1XPN1F", # not used
                    "service":"UWkyb5W46zn",
                    "quantity":"nJ0sT27I9LL",
                    "price":"uwGg814hDhB",
                    "deductibleAmount":"aD2rD5VCsRt",
                    "exeedingCeilingAmount":"gUanr8YW9Kj",
                    "renumeratedAmount": "WyAw53dfnMj", # not used
                    "seqId":"QmuynKAhycW"
                    }
            }
        },
        
        "attributes" : {
            "insuranceId":"g54R38QNwEi", # Not part of the basic package
            "claimAdministrator":"wDBF7RjuEyp",
            "claimNumber" : "Z4yrjMuGkeY", # salted for privacy reason
            "diagnoseMain":"AAjWdVvBwtE",
            "diagnoseSec1":"aEWuz6qyTs6",
            "diagnoseSec2":"yoULFOTtmoP",
            "diagnoseSec3":"gRLd9ezU69M",
            "diagnoseSec4":"cPbpCJnkrci",
            "VisitType": "Hxyr4f36WHF"
        }
    },"fundingProgram" : {
        "id" : "xB6Q2acQejV",
        "stages":{
            "funding" : {
                "id" : "EPFYYYVuiSw",
                "dataElements": {
                    "product":"NAdBLHAdOGv",
                    "amount":"IHim9F2Hzj4", 
                    }
            }
        }
    }
}
# Population on location : id: "UbpmYBEmuwK" TBD


class Dhis2Config(AppConfig):
    name = MODULE_NAME

    def ready(self):
        from core.models import ModuleConfiguration
        
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__configure_module(cfg)

    def __configure_module(self, cfg):
        ModuleConfiguration.build_configuration(cfg)
        logger.info('Module %s configured successfully', MODULE_NAME)

# To be replaced by optionset

    # "genderCodes": {
    #     "M" : "Male",
    #     "F" : "Female",
    #     "O" : "Other",
    #     "U" : "Unknown" # Default
    # },
    # "professionCodes": {
    #     "4" : "Household",
    #     "2" : "Employee",
    #     "1" : "Selfemployee",
    #     "0" : "Other" # default
    # },
    # "booleanCodes":{
    #     "0" : "No", # Default
    #     "1" : "Yes"
    # },  
    # "groupTypeCodes":{
    #     "C" : "Council",
    #     "O" : "Organisation",
    #     "H" : "Household",
    #     "P" : "Priests",
    #     "S" : "Students",
    #     "T" : "Teachers",
    #     "X" : "Other" # Default
    # },
    # "educationCodes":{
    #     "1" : "Nursery",
    #     "2" : "Primary school",
    #     "3" : "Secondary school",
    #     "4" : "Secondary school",
    #     "5" : "Secondary school",
    #     "6" : "Secondary school",
    #     "7" : "University",
    #     "8" : "Postgraduate studies",
    #     "9" : "PhD",
    #     "10" : "Other" # default        
    # }
