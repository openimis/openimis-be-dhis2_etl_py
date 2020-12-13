from django.apps import AppConfig


DEFAULT_CFG = {
    "salt":"LeSalt",
    "genderCodes": {
        "M" : "Male",
        "F" : "Female",
        "O" : "Other",
        "U" : "Unknown" # Default
    },
    "professionCodes": {
        "4" : "Household",
        "2" : "Employee",
        "1" : "Selfemployee",
        "0" : "Other" # default
    },
    "booleanCodes":{
        "0" : "No", # Default
        "1" : "Yes"
    }, 
    "maritalStatusCodes":{
        "M" : "Maried",
        "D" : "Divorced",
        "W" : "Widowed",
        "S" : "Single" # Default
    }, 
    "groupTypeCodes":{
        "C" : "Council",
        "O" : "Organisation",
        "H" : "HouseHold",
        "P" : "Priests",
        "S" : "Students",
        "T" : "Teachers",
        "X" : "Other" # Default
    },
    "educationCodes":{
        "1" : "Nursery",
        "2" : "Primary school",
        "3" : "Secondary school",
        "4" : "Secondary school",
        "5" : "Secondary school",
        "6" : "Secondary school",
        "7" : "University",
        "8" : "Postgraduate studies",
        "9" : "PhD",
        "10" : "Other" # default        
    }, 
    "default_page_size":"250",
    "insureeProgram" : {
        "id" : "IR5BiEXrBD7",
        "teiType":"EoBGArVCQ69",
        "stages": [
            "policy" : {
                "id":"DVRNDUNwI9s",
                "dataElements": {
                    "policyStage":"j028KRFsjx6", # categoryCombo "bjDvmb4bfuf"
                    "policyStatus":"Q0pEucwW60Z",
                    "prodcut":"NAdBLHAdOGv",
                    "policyId":"NtslGBEMyMy", 
                    "PolicyValue":"mVeMk0sNLZb",
                    "expirityDate":"RzgHQtgsmfB" # note used
                    }
            }
        ],
        "attributes" : [
            "poverty" : "WeLouCfrfoF",
            "CHFId":"HaVpe5WsCRl", # should not use it
            "insuranceId":"g54R38QNwEi", # Salted data for privay reason
            "insureeId":"e9fOa40sDwR",  # should not use it
            "familiyId":"DvT0LSMDW2f",
            "dob":"woZmnhwGvu6",
            "education":"pWV8uthRZVY",
            "groupType":"QnAQO4Kd4I3",
            "firstName":"vYdz8EjQJe0", # not used for privacy reason
            "firstServicePoint":"GZ6zgXS25VH",
            "gender":"QtkHTKL4EsU",
            "isHead":"siOTMqr9kw6",
            "identificationId":"MFPEijajdy7", # not used for privacy reason
            "identificationSource":"jOnARr3GARW", # not used for now
            "profession":"zy5Br9ZEDLY",
            "maritalSatus":"vncvDog0YwP",
            "phoneNumber": "r9hJ7SJbVvx", # TBC
        ]
    },    "ClaimProgram" : {
        "id" : "vPjOO7Jl6jC",
        "stages": [
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
        ],
        "attributes" : [
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
    ]
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
        logger.info('Module $s configured successfully', MODULE_NAME)
