import pytz
from django.utils.timezone import localtime
from datetime import datetime, date


def seconds_to_minutes(seconds) -> str:
    formatted_str = '{:02} min(s) {:02} sec(s)'.format(seconds // 60, seconds % 60) \
        if seconds > 60 \
        else '{:02} sec(s)'.format(seconds)
    return formatted_str


def now_in_tz(tz: str) -> datetime:
    return localtime(timezone=pytz.timezone(tz))


def time_today_in_tz(timezone: str, hour, minute=0, second=0) -> datetime:
    _now_in_tz = now_in_tz(timezone)
    return _now_in_tz.replace(hour=hour,
                              minute=minute,
                              second=second,
                              microsecond=0)


def today_in_tz(tz: str) -> date:
    return now_in_tz(tz).date()
