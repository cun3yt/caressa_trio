from alexa.models import AUser
from icalendar import Calendar, Event
from datetime import datetime
import pytz


def run():
    user_id = 1

    user = AUser.objects.get(id=user_id)

    # todo admin facility to create a schedule for the users?
    cal = Calendar()
    cal.add('dtstart', datetime.now())
    cal.add('summary', 'schedule of user:{}'.format(user_id))

    event = Event()
    event.add('summary', 'MedicalEngine')
    event.add('dtstart', datetime(2018, 4, 4, 0, 0, 0, tzinfo=pytz.utc))
    event.add('dtend', datetime(2018, 4, 4, 23, 59, 59, tzinfo=pytz.utc))
    event.add('rrule', {'freq': 'daily'})

    cal.add_component(event)
    user.engine_schedule = cal.to_ical().decode(encoding='UTF-8')
    user.save()
