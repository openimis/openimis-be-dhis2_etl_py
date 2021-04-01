# DHIS2 enums
# Copyright Patrick Delcoix <patrick@pmpd.eu>

from enum import Enum, IntEnum


class ValueType(str, Enum):
    time = "TIME"
    dateTime = "DATETIME"
    date = "DATE"
    age = "AGE"
    phoneNumber = "PHONE_NUMBER"
    email = "EMAIL"
    yesNo = "BOOLEAN"
    yesOnly = "TRUE_ONLY"
    number = "NUMBER"
    integer = "INTEGER"
    positiveInteger = "INTEGER_POSITIVE"
    negativeInteger = "INTEGER_NEGATIVE"
    positiveZeroInteger = "INTEGER_ZERO_OR_POSITIVE"
    percentage = "PERCENTAGE"
    unitInterval = "UNIT_INTERVAL"
    text = "TEXT"
    longText = "LONG_TEXT"
    letter = "LETTER"
    file = "FILE_RESOURCE"
    orgUnt = "ORGANISATION_UNIT"
    trackerAssociate = "TRACKER_ASSOCIATE"
    userName = "USERNAME"
    coordniate = "COORDINATE"
    image = "IMAGE"
    url = "URL"

class Direction(str, Enum):
    ascending ="ASCENDING" 
    descending = "DESCENDING"

class FeatureType(str, Enum):
    multiPolygon = "MULTI_POLYGON"
    none = "NONE" 
    point = "POINT" 
    polygon = "POLYGON"
    symbol = "SYMBOL"

class MessageType(str, Enum):
    private = "PRIVATE"
    system = "SYSTEM" 
    ticket = "TICKET" 
    validationResult = "VALIDATION_RESULT"

class AccessLevel(str, Enum):
    audited = "AUDITED"
    closed = "CLOSED"
    open = "OPEN" 
    protected = "PROTECTED"

class JobStatus(str, Enum):
    completed = "COMPLETED"
    disabled = "DISABLED"
    failed = "FAILED"
    notStarted = "NOT_STARTED" 
    running = "RUNNING"
    scheduled = "SCHEDULED"
    stoped = "STOPPED"

class AppStatus(str, Enum):
    approved = "APPROVED"
    deletion_in_progress = "DELETION_IN_PROGRESS"
    installation_failed = "INSTALLATION_FAILED"
    invalid_bundled_app_override = "INVALID_BUNDLED_APP_OVERRIDE"
    invalid_core_app = "INVALID_CORE_APP"
    invalid_manifest_json = "INVALID_MANIFEST_JSON"
    invalid_zip_format = "INVALID_ZIP_FORMAT"
    missing_manifest = "MISSING_MANIFEST"
    missing_system_base_url = "MISSING_SYSTEM_BASE_URL"
    namespace_taken = "NAMESPACE_TAKEN"
    not_approved = "NOT_APPROVED"
    not_found = "NOT_FOUND"
    ok = "OK"
    pending = "PENDING"

class GatewayStatus(str, Enum):
    authentication_failed = "AUTHENTICATION_FAILED"
    encoding_failure = "ENCODING_FAILURE"
    failed = "FAILED"
    no_default_gateway = "NO_DEFAULT_GATEWAY"
    no_gateway_configuration = "NO_GATEWAY_CONFIGURATION"
    no_recipient = "NO_RECIPIENT"
    pending = "PENDING"
    processing = "PROCESSING"
    queued = "QUEUED"
    result_code_0 = "RESULT_CODE_0"
    result_code_1 = "RESULT_CODE_1"
    result_code_200 = "RESULT_CODE_200"
    result_code_201 = "RESULT_CODE_201"
    result_code_202 = "RESULT_CODE_202"
    result_code_207 = "RESULT_CODE_207"
    result_code_22 = "RESULT_CODE_22"
    result_code_23 = "RESULT_CODE_23"
    result_code_24 = "RESULT_CODE_24"
    result_code_25 = "RESULT_CODE_25"
    result_code_26 = "RESULT_CODE_26"
    result_code_27 = "RESULT_CODE_27"
    result_code_28 = "RESULT_CODE_28"
    result_code_40 = "RESULT_CODE_40"
    result_code_400 = "RESULT_CODE_400"
    result_code_401 = "RESULT_CODE_401"
    result_code_402 = "RESULT_CODE_402"
    result_code_403 = "RESULT_CODE_403"
    result_code_404 = "RESULT_CODE_404"
    result_code_405 = "RESULT_CODE_405"
    result_code_410 = "RESULT_CODE_410"
    result_code_429 = "RESULT_CODE_429"
    result_code_503 = "RESULT_CODE_503"
    result_code_504 = "RESULT_CODE_504"
    sent = "SENT"
    service_not_available = "SERVICE_NOT_AVAILABLE"
    smpp_session_failure = "SMPP_SESSION_FAILURE"
    sms_disabled = "SMS_DISABLED"
    success = "SUCCESS"


class EnrollmentStatus(str, Enum):
    active = "ACTIVE"
    cancelled = "CANCELLED"
    completed = "COMPLETED"

class EventStatus(str, Enum):
    active = "ACTIVE" 
    completed = "COMPLETED"
    overdue = "OVERDUE"
    schedule = "SCHEDULE"
    skipped = "SKIPPED"
    visited = "VISITED"

class FileRessourceDomain(str, Enum):
    dataValue = "DATA_VALUE"
    document = "DOCUMENT"
    messageAttachment = "MESSAGE_ATTACHMENT"
    pushAnalysis = "PUSH_ANALYSIS" 
    userAvatar = "USER_AVATAR"

class DateUnitType(str, Enum):
    biMonthly = "BI_MONTHLY"
    biWeekly = "BI_WEEKLY"
    daily = "DAILY"
    financialApril = "FINANCIAL_APRIL"
    financialJuly = "FINANCIAL_JULY"
    financialNovember = "FINANCIAL_NOVEMBER"
    financialOctober = "FINANCIAL_OCTOBER"
    monthly = "MONTHLY"
    quarterly = "QUARTERLY" 
    sixMonthly = "SIX_MONTHLY" 
    sixMonthlyApril = "SIX_MONTHLY_APRIL" 
    sixMonthlyNovember = "SIX_MONTHLY_NOVEMBER" 
    weekly = "WEEKLY"
    weeklySaturday = "WEEKLY_SATURDAY"
    weeklySunday = "WEEKLY_SUNDAY"
    weeklyThursday = "WEEKLY_THURSDAY"
    weeklyWednesday = "WEEKLY_WEDNESDAY"
    yearly = "YEARLY"



class PreheatIdentifier(str, Enum):
    auto = "AUTO"
    code = "CODE"
    uid = "UID"

class MatchMode(str, Enum):
    anywhere = "ANYWHERE"
    end = "END"
    exact = "EXACT"
    start = "START"

class MergeMode(str, Enum):
    merge = "MERGE"
    mergeAlways = "MERGE_ALWAYS"
    mergeIfNotNull = "MERGE_IF_NOT_NULL"
    none = "NONE" 
    replace = "REPLACE"

class DomainType(str, Enum):
    aggregate = "AGGREGATE"
    tracker = "TRACKER"

class AgregationType(str, Enum):
    sum = "SUM"
    average = "AVERAGE"
    averageOrgUnit = "AVERAGE_SUM_ORG_UNIT"
    count = "COUNT"
    standardDeviation = "STDDEV"
    variance = "VARIANCE"
    min = "MIN"
    max = "MAX"
    none = "NONE"

class ImportStrategy(str, Enum):
    create = "CREATE"
    createUpdate = "CREATE_AND_UPDATE"
    delete = "DELETE"
    deletes = "DELETES"
    new = "NEW"
    newUpdate = "NEW_AND_UPDATES"
    sync = "SYNC"
    update = "UPDATE"
    updates = "UPDATES"