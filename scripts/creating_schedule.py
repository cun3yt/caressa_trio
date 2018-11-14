from alexa.models import AUser
from senior_living_facility.models import SeniorLivingFacility
from icalendar import Calendar, Event
from icalevents.icalevents import events as query_events
from datetime import date, datetime, timedelta
import pytz


timezone_str = 'America/Los_Angeles'


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


def events_today():
    tz = pytz.timezone('America/Los_Angeles')

    print('fn... query_all_day')
    facility = SeniorLivingFacility.objects.all()[0]
    calendar = facility.calendar.encode(encoding='UTF-8')

    now = datetime.now(tz)

    events = query_events(string_content=calendar,
                          start=(datetime(now.year, now.month, now.day, 0, 0, 0,
                                          tzinfo=tz)),
                          end=(datetime(now.year, now.month, now.day, 23, 59, 59,
                                        tzinfo=tz)),
                          fix_apple=True)

    all_day_events = [event for event in events if event.all_day]
    hourly_events = [event for event in events if not event.all_day]

    now_in_tz = now.astimezone(tz)
    today_summary = "Today is {}. ".format(now_in_tz.strftime('%B %d %A'))

    today_summary = "{} Here is today's schedule at {}: ".format(today_summary, facility.name)

    for event in hourly_events:
        start_in_tz = event.start.astimezone(tz)
        event_txt = "At {}: {}. ".format(start_in_tz.strftime('%I:%M %p'), event.summary)
        today_summary = "{}{}".format(today_summary, event_txt)

    if len(all_day_events) == 1:
        today_summary = "{}There is a special thing for today: {}".format(today_summary, all_day_events[0].summary)
    elif len(all_day_events) > 1:
        today_summary = "{}There are {} special things for today: ".format(today_summary, len(all_day_events))
        for (no, event) in enumerate(all_day_events, start=1):
            today_summary = "{} ({}) {}.".format(today_summary, no, event.summary)

    print(today_summary)


def run(*args):
    fn = args[0]
    print("running {}".format(fn))
    globals()[fn]()
