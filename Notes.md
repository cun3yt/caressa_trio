# Learning Notes

## Alexa
* session attributes are overwritten once you turn it back it on the response.
* request types:
    * LaunchRequest
    * IntentRequest
    * SessionEndedRequest
* All requests include at the top level:
    * version, 
    * context,
    * request objects 
* The session object is included for all standard requests (LaunchRequest, IntentRequest, and SessionEndedRequest), but it is not included for AudioPlayer, VideoApp, or PlaybackController requests.
* routing must be based on "user state" X "last session state" X "session state" X "request"
* Context is always available in the request, but session is not guaranteed. This can also be stated as not all requests are sent in the context of a session.
 
### Dialog Interface
* It provides the two-way communication
* Directives:
    * Dialog.Delegate
    * Dialog.ElicitSlot
    * Dialog.ConfirmSlot
    * Dialog.ConfirmIntent
* IntentRequest contains `dialogState`, possible values:
    * STARTED
    * IN_PROGRESS

# Scripts
* django-extensions provides management command: runscript. Example:
    * scripts/ module on the root.
    * ./manage.py runscript reminder-notification [--script-args arg1 arg2 ...]
    * the script file must have run() function, it can accept postional arguments.
    * the working directory policy is set with setting: RUNSCRIPT_CHDIR_POLICY

## Django
* add index to the created/modified fields: https://stackoverflow.com/questions/33174680/django-add-index-to-meta-field
    * outside of class scope: `AlexaEngineLog._meta.get_field('modified').db_index = True`

## Queue
* Need to run pq.create()
    from psycopg2 import connect
    from pq import PQ    
    conn = connect('host={host} dbname={dbname} user={user}'.format(host='xx', dbname='xx', user='xx'))
    pq = PQ(conn, table='alexa_conversation_queue')
    pq.create


## Python specific
* string to byte:
    * stringThing.encode(encoding='UTF-8')
* Byte to string:
    * cal.to_ical().decode(encoding='UTF-8')

# Time Work
* tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
    # event.add('rrule', u  'FREQ=YEARLY;INTERVAL=1;COUNT=10'
* So they must have changed their format to a dictionary instead
    ev.add('rrule', {'freq': 'daily'} works
* http://dateutil.readthedocs.io/en/stable/rrule.html

* example
    from dateutil import *
    r = rrule(YEARLY, bymonth=1, dtstart=parse('19980101'), until=parse('20000131'))
    r_as_string = str(r)
    rs = rrulestr(r_as_string)
    list(rs)

* from icalendar import Event
* ev = Event()
* ev.add('rrule', {'freq': 'daily'}

* evs = icalevents.events(string_content=sch, start=date(2018, 5, 1), end=date(2018, 5, 5))
* evs = icalevents.events(string_content=sch.encode(encoding='UTF-8'), start=start, end=end)
* len(evs)
* evs[0].start
* evs[0].end
* evs[0].time_left()


# Questions

* bir ana intent olsa ve donen slotlarla dialog yonetilse, boyle bir sey mumkun mu?
* ilk iki makale su ana kadar en mantikli intent kullanimini sunuyor.
* yes/no intent olarak kullanilabilir.

# Tried But moved away
* these two packages don't work well with each other:
    * transitions==0.6.4
    * jsonpickle==0.9.6

* Installed graphviz:
    * brew install graphviz

* Reverse SSH for global-local server:
    * alias servo='ssh -R letatio.serveo.net:80:localhost:9900 serveo.net'
   
* Port 80 Used by (from http://bit.ly/2GN2wEJ):
    * sudo lsof -i tcp:80
    * netstat -vanp tcp | grep 80 

* Multiple models with the same database table: http://bit.ly/2u9Xako
* Making `TimeStampedModel`s fields indexed (from `model_utils.models`):
    * Request._meta.get_field('created').db_index = True
    * Request._meta.get_field('modified').db_index = True