import datetime
from dataclasses import dataclass
from typing import Callable, Any, List


@dataclass
class SyncFunction:
    name: str
    sync_function: Callable[[datetime.datetime, datetime.datetime], Any]
    is_enabled: bool

    def sync(self, from_date: datetime.datetime, to_date: datetime.datetime):
        return self.sync_function(from_date, to_date)


class DailySync:
    def __init__(self, sync_functions: List[SyncFunction]):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.from_date = datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day)
        self.to_date = self.from_date + datetime.timedelta(days=1)
        self.sync_functions = sync_functions

    def sync(self):
        for function in self.sync_functions:
            if function.is_enabled:
                function.sync(self.from_date, self.to_date)
