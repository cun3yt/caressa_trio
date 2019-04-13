import pytz
from django.utils.timezone import localtime
from datetime import datetime, date


def seconds_to_minutes(seconds) -> str:
    formatted_str = '{:02} min(s) {:02} sec(s)'.format(seconds // 60, seconds % 60) \
        if seconds > 60 \
        else '{:02} sec(s)'.format(seconds)
    return formatted_str


def time_today_in_tz(timezone: str, hour, minute=0, second=0) -> datetime:
    now_in_tz = localtime(timezone=pytz.timezone(timezone))
    return now_in_tz.replace(hour=hour,
                             minute=minute,
                             second=second,
                             microsecond=0)


def today_in_tz(tz: str) -> date:
    return localtime(timezone=pytz.timezone(tz)).date()
