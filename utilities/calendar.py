from icalendar import Calendar
from datetime import datetime


def create_empty_calendar(start=None, summary=None):
    start = start if start else datetime.now()
    summary = summary if summary else 'Not Specified'

    cal = Calendar()
    cal.add('dtstart', start)
    cal.add('summary', summary)
    return cal.to_ical().decode(encoding='UTF-8')
