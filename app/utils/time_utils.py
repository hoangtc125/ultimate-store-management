from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta
import time
from app.core.constants import DateTime


def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())

def to_timestamp(timestamp: datetime) -> int:
    return int(timestamp.timestamp())

def get_timestamp_after(current_time: Optional[int] = None, **args):
    current_datetime = datetime.fromtimestamp(current_time) if current_time else datetime.now()
    datetime_after = current_datetime + relativedelta(**args)
    return int(datetime_after.timestamp())

def datetime_str_to_timestamp(date: str, format: str = DateTime.DATE_FORMAT) -> int:
    return int(time.mktime(datetime.strptime(date, format).timetuple()))

def to_datestring(timestamp: int, date_format = DateTime.DATE_FORMAT) -> str:
    return datetime.fromtimestamp(timestamp).strftime(date_format)

def validate_format(time_str: str, format: str = DateTime.DATETIME_FORMAT):
    try:
        datetime.strptime(time_str, format)
        return True
    except:
        return False

def get_current_date() -> int:
    return datetime_str_to_timestamp(datetime.now().strftime(DateTime.DATE_FORMAT))
