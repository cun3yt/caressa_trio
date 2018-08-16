def seconds_to_minutes(seconds) -> str:
    formatted_str = '{:02} min(s) {:02} sec(s)'.format(seconds // 60, seconds % 60) \
        if seconds > 60 \
        else '{:02} sec(s)'.format(seconds)
    return formatted_str
