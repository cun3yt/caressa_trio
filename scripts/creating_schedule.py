from alexa.models import AUser
from senior_living_facility.models import SeniorLivingFacility
from icalendar import Calendar, Event
from icalevents.icalevents import events as query_events
from datetime import date, datetime, timedelta
import pytz


def create_calendar_for_user():
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


def create_calendar_for_senior_living_facility():
    facility = SeniorLivingFacility.objects.all()[0]

    cal = Calendar()
    cal.add('dtstart', datetime.now())
    cal.add('summary', 'Fremont Brookdale Calendar')

    # event = Event()
    # event.add('summary', 'Name Tag Day')
    # event.add('dtstart', date(2018, 10, 10))
    # event.add('dtend', date(2018, 10, 10))
    # event.add('rrule', {'freq': 'daily'})
    # cal.add_component(event)
    #
    # event = Event()
    # event.add('summary', 'YOGA w/ Nancy')
    # event.add('location', 'Activity Room')
    # event.add('dtstart', datetime(2018, 10, 10, 11, 0, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # event.add('dtend', datetime(2018, 10, 10, 12, 0, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # cal.add_component(event)

    # event = Event()
    # event.add('summary', 'Blood Pressure')
    # event.add('location', 'Activity Room')
    # event.add('dtstart', datetime(2018, 10, 10, 13, 0, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # event.add('dtend', datetime(2018, 10, 10, 14, 0, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # cal.add_component(event)
    #
    # event = Event()
    # event.add('summary', '"My Story" Write & Share')
    # event.add('location', 'Media Room')
    # event.add('dtstart', datetime(2018, 10, 10, 13, 15, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # event.add('dtend', datetime(2018, 10, 10, 14, 15, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
    # cal.add_component(event)

    hours = range(0, 24)
    halves = range(0, 60, 30)

    for hour in hours:
        for half in halves:
            event = Event()
            event.add('summary', 'Event at {}:{}'.format(hour, "00" if half==0 else half))
            event.add('location', 'Activity Room')
            event.add('dtstart', datetime(2018, 10, 10, hour, half, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
            event.add('dtend', datetime(2018, 10, 10, hour, 30 if half == 0 else 0, 0, tzinfo=pytz.timezone('America/Los_Angeles')))
            event.add('rrule', {'freq': 'daily'})
            cal.add_component(event)

    facility.calendar = cal.to_ical().decode(encoding='UTF-8')
    facility.save()


def query_calendar():
    print('fn... query_calendar')

    facility = SeniorLivingFacility.objects.all()[0]
    calendar = facility.calendar.encode(encoding='UTF-8')
    events = query_events(string_content=calendar,
                          start=(datetime.now(pytz.timezone('America/Los_Angeles')) + timedelta(minutes=30)),
                          end=(datetime.now(pytz.timezone('America/Los_Angeles')) + timedelta(minutes=35)),
                          fix_apple=True)

    print(len(events))

    for event in events:
        print(" >> event in question: {}".format(event.summary))
        print("    this is the event summary: {}".format(event.summary))


def run(*args):
    fn = args[0]
    print("running {}".format(fn))
    globals()[fn]()
