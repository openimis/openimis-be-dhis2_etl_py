import datetime
import hashlib
# import the logging library
import logging
import re




# Get an instance of a logger
logger = logging.getLogger('openIMIS')



def toDatetimeStr(dateIn):
    if dateIn is None:
        return None
    elif isinstance(dateIn, datetime.datetime):
        return (dateIn.isoformat() + ".000")[:23]
    elif isinstance(dateIn, datetime.date):
        return (dateIn.isoformat() + "T00:00:00.000")[:23]
    elif isinstance(dateIn, str):
        regex = re.compile("^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3,6})?$")
        if regex.match(dateIn):
            return (dateIn + ".000")[:23]
        regex = re.compile("^\d{4}-\d{2}-\d{2}$")
        if regex.match(dateIn):
            return (dateIn + "T00:00:00.000")[:23]
        else:
            return None
    else:
        return None


def toDateStr(dateIn):
    if dateIn is None:
        return None
    elif isinstance(dateIn, datetime.datetime) or isinstance(dateIn, datetime.date):
        return dateIn.isoformat()[:10]
    elif isinstance(dateIn, str):
        regex = re.compile("^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{3,6})?)?$")
        if regex.match(dateIn):
            return dateIn[:10]
        else:
            return None
    else:
        return None


def build_dhis2_id(uuid, salt=""):
    regex = re.compile("^[a-fA-F0-9\-]{32}$")
    tmp_uuid = str(uuid).replace('-','')
    if (not regex.match(str(tmp_uuid))):
        # in case the table doesn't have uuid but id only
        # the salt is important becasue the DHIS2 capture app doesn't support
        # 2x the same id for metadata, event if it's from different kind
        salteduuid = salt + str(uuid)
        tmp_uuid = hashlib.md5(salteduuid.encode()).hexdigest()
    
    DHIS2IDCharDict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 
            16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 
            28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 
            40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 
            52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z', 62: 'A', 63: 'B'}
    dhis2_id = ''

    # trasform 2 hex (256) in to 0-9a-zA-Z(62)  for 22 symbol on 32 --> data loss = 1-(62/256*22/36) = 83,4%
    for x in range(11):
        int0 = int(tmp_uuid[0:1], 16)
        int1 = int(tmp_uuid[1:2], 16)
        char = int0 * 4 + int(int1 / 4)
        if x == 0 and char < 10:
            char += 10
        dhis2_id += DHIS2IDCharDict[char]
        tmp_uuid = tmp_uuid[2:]
    return dhis2_id[0:11]


def clean_code(code):
  
    return (re.sub(r"[^a-zA-Z0-9\*]", "_",code )).upper()
