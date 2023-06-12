from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import dateutil
import isodate as isodate
from dhis2_etl.models.adx.data import Period


class PeriodType(ABC):
    @abstractmethod
    def build_period(self, str_representation: str, **kwargs) -> Period:
        pass

    @abstractmethod
    def _build_repr(self, **kwargs) -> str:
        pass


class PeriodParsingException(BaseException):
    def __init__(self, str_repr, parser, err_msg):
        self.str_repr = str_repr
        self.parser = parser
        self.err_msg = err_msg
        msg = f"Failed to parse str representation of period `{str_repr}` with parser `{parser}`, reason:\n\t{err_msg}"
        super().__init__(msg)


class ISOFormatPeriodType(PeriodType):     # W3C / ISO 8601 time interval : date/duration or datetime/duration
    TYPE = "ISO8601"

    def build_period(self, str_representation: str, **kwargs) -> Period:
        try:
            date_and_duration = str_representation.split('/')
            if len(date_and_duration) != 2:
                raise PeriodParsingException(
                    str_representation, type(self).__name__, "Invalid format of string, should be `datetime/duration`")

            start_date, duration = date_and_duration
            start_date = self.__iso_date_to_datetime(start_date)
            duration = self.__iso_duration_to_time_delta(duration)
            to_date = start_date + duration
            return Period(
                period_type=self.TYPE,
                from_date=start_date,
                to_date=to_date,
                representation=str_representation
            )
        except isodate.isoerror.ISO8601Error as e:
            raise PeriodParsingException(str_representation, type(self).__name__, str(e)) from e

    def _build_repr(self, **kwargs) -> str:
        pass

    def __iso_duration_to_time_delta(self, iso_duration) -> timedelta:
        return isodate.parse_duration(iso_duration)

    def __iso_date_to_datetime(self, iso_date) -> datetime:
        return dateutil.parser.parse(iso_date)
