from abc import ABC
import re

class BaseDHIS2Converter(ABC):

    @classmethod
    def to_tei_obj(cls, obj):
        raise NotImplementedError('`to_tei_obj()` must be implemented.')  # pragma: no cover
 
    @classmethod
    def to_enrolment_obj(cls, obj):
        raise NotImplementedError('`to_enrolment_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_event_obj(cls, obj):
        raise NotImplementedError('`to_event_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_dataelement_obj(cls, de_id, obj):
        raise NotImplementedError('`to_data_element_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def to_dataset_obj(cls, de_id, obj):
        raise NotImplementedError('`to_data_set_obj()` must be implemented.')  # pragma: no cover

    @classmethod
    def build_dhis2_identifier(cls, identifiers, imis_object):
        if hasattr(imis_object,'uuid') and imis_object.uuid is not None:
            DHIS2IDCharDict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 
                16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 
                28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 
                40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 
                52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z', 62: 'A', 63: 'B'}
            dhis2_id = ''
            #remove the "-
            tmp_uuid = imis_object.uuid.replace('-','')
            # trasform 2 hex (256) in to 0-9a-zA-Z(52)  for 22 symbol on 36 --> data loss = 1-(52/256*22/36) = 87.5%
            for x in range(18):
                int0 = int(tmp_uuid[0:1] ,16)
                int1 = int(tmp_uuid[1:2] ,16)
                char = int0*4+int(int1/4)
                if x = 0 and char < 10:
                    char += 10
                dhis2_id +=  DHIS2IDCharDict[char]
                
            identifier = cls.build_fhir_identifier(dhis2_id[0:11],
                                                   R4IdentifierConfig.get_fhir_identifier_type_system(),
                                                   R4IdentifierConfig.get_fhir_dhis2_id_type_code())
            identifiers.append(identifier)