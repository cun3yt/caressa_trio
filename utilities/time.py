import pytz
from django.utils.timezone import localtime


def seconds_to_minutes(seconds) -> str:
    formatted_str = '{:02} min(s) {:02} sec(s)'.format(seconds // 60, seconds % 60) \
        if seconds > 60 \
        else '{:02} sec(s)'.format(seconds)
    return formatted_str


def time_today_in_tz(timezone, hour, minute=0, second=0):
    now_in_tz = localtime(timezone=pytz.timezone(timezone))
    return now_in_tz.replace(hour=hour,
                             minute=minute,
                             second=second,
                             microsecond=0)
