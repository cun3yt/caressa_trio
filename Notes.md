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
    

# Starting a Project & App

* virtualenv -p python3 ./venv-practice
* activating environment: source ./venv-practice/bin/activate
* create requirements.txt document and put necessary package references such as Django==2.0.0
* run `pip install -r requirements.txt`
* create an app: ./manage.py startapp myapp
* add app to the installed applications in settings.py
* create super user: ./manage.py createsuperuser

# Heroku Setup
* Current setup for heroku push: `git push heroku master`
* logs: heroku logs -a <app-name> -t
* bash: heroku run bash -a <app-name>


# Notes on Models
* The base model is django.db.model
* model.CharField requires max_length attribute while model.TextField does not. In PostgreSQL it doesn't matter which one you use.
* Important attributes: `null`, `blank` and `default`
    * if null=True, empty values will be stored as null values. Don't use in string fields. This is purely database related.
    * if blank=True, field is allowed to be blank. `blank` is validation-related in the forms.
    * default is either unmutable type or callable. Current object-dependent default function is a feasible due to serialization, so you need to treat it as a stand-alone auxiliary function which gets no argument. If you need current object-dependent (or other objects-dependent) value writing the logic on save signal will be better (e.g. django.db.models.signals.pre_save and django.db.models.signals.post_save). Some usages of default function can be other parameters-based value usage, like "time trigger". default doesn't put default value to the database table field (at least not in sqlite).
    * random identifier can be created: `from uuid import uuid4`
    * generating random id for a field:
        import uuid
        from django.db import models

        class MyUUIDModel(models.Model):
            id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
            # other fields
    * when primary_key=True property/value is added to an attribute, the model doesn't have an auto increment ID field. 
* `def __str__(self)` helps you see the content of the object easier.
* create migrations: ./manage makemigrations
* squashing migrations is possible, too.
* apply migration: ./manage migrate
* put django_extensions to installed apps in settings.py
* see available manage cmds: ./manage.py --help
* ./manage.py shell_plus
* In order not to have problem with auto-added `id` fields in Pycharm enable Django support. Go to PyCharm -> Preferences -> Languages & Frameworks -> Django and then check Enable Django Support.

# Notes on Model Signals

* django.db.models.signals & django.dispatch.receiver
* Long form:
def set_default_name_for_todo(sender, instance, created, **kwargs):
    if created and instance.name == '':
        instance.name = 'default'
        instance.save()
signals.post_save.connect(set_default_name_for_todo, sender=TodoX)

* Short form:
@receiver([signals.post_save], sender=TodoX)
def log(sender, instance, **kwargs):
    print("save operation for {} on id: {}".format(sender, instance))
* App configuration class' ready function is the best place to register signals. In order to do that you need to set `default_app_config` to the dotted location of the config object:
    default_app_config = 'apps.todo.apps.TodoConfig' #noqa

# Notes on Views & Forms
* generic views gives ability of creating predefined views like list/create etc. Example is django.views.generic.edit.[CreateView/FormView], django.views.generic.list.ListView
* Forms can be based on nothing (django.forms.Form) or a model (django.forms.ModelForm).
* reverse_lazy is the way to go for getting url from the name of the url.
* validations are added to the model fields.
* forms need to be submitted to the same url they are initially rendered. This gives the ability to render the validation errors. But there is success_url all the time.
* widgets are used on the form level for specifying the input type, attributes of the input field.
* to list the items in template context: <pre>{% filter force_escape %}{{debug}}{% endfilter %}</pre>
* Decorating Views: https://docs.djangoproject.com/en/2.0/topics/class-based-views/intro/#decorating-class-based-views
* Initial data for form: JournalForm(initial={'tank': 123}) 

# Arranging Viewport for Mobile
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

# Template
* Template location by default: `<app-folder>/templates/`
* For generic templates the template location: `<app-name>/templates/<app-name>`
* Template Extension:
For base: {% block title %}Default Content Here...{% endblock %}
For extender:
    {% extends 'template.html' %}
    {% block title %}Updated Content Here...{% endblock %}

# Middleware
* Define a function that gets a response argument and returns a callable.
* Or define a class which is instantiated with response and is callable with `__call__` function. __call__ fnc makes the class callable.

# Request Params, Cookies & Sessions
* Request params are accessible: request.GET.get('xyz')
* Cookies are accessible: request.COOKIES.get('xyz')
* Cookies are set on the response object: response.set_cookie('xyz', 1)

# Created/Modified with django-model-utils
* Used like this:
from model_utils.models import TimeStampedModel
class Todo(TimeStampedModel):
  pass

# Flash Messages (The Message Framework)
  in view:
  from django.contrib import messages
  messages.info(request, 'Created Successfully')

  in template:
  {% if messages %}
    <ul class="messages">
        {% for message in messages %}
        <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
        {% endfor %}
    </ul>
  {% endif %}

# Using Django Revision Package for Version Control on Data Objects
* This needs to run for every model registered: ./manage.py createinitialrevisions
* Delete recovery is out of box. If you need version control for instance changes, enabling it for models manually or automatically (automatic: Use middleware 'reversion.middleware.RevisionMiddleware').
* Register Model: http://django-reversion.readthedocs.io/en/stable/api.html#registering-models
    from django.db import models
    import reversion
    @reversion.register()
    class YourModel(models.Model):
        pass
        
* Register admin. If admin registration is used model registration is automatic (according to the documentation).
* `History` link is added to the admin pages.
* Additionally Install reversion_compare to see changes between versions easily:
    from django.contrib import admin
    from reversion_compare.admin import CompareVersionAdmin
    from apps.todo.models import Todo
    @admin.register(Todo)
    class TodoAdmin(CompareVersionAdmin):
        pass

# Time Manipulations
* Set the timezone in settings.py.
* Aware current UTC: now = datetime.now(timezone.utc)
* Time math: now + timedelta(hours=12)
* Humanization: Add 'django.contrib.humanize' to installed applications list, load humanize in the template; then use filters like "naturaltime".

# Mobile Specific
* Mobile like feeling when saved to the home screen: <meta name="apple-mobile-web-app-capable" content="yes"> it is from this link: https://developers.google.com/web/fundamentals/native-hardware/fullscreen/
* There may be some hidden gems here: https://developer.apple.com/library/content/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html

# Scripts
* django-extensions provides management command: runscript. Example:
    * scripts/ module on the root.
    * ./manage.py runscript reminder-notification [--script-args arg1 arg2 ...]
    * the script file must have run() function, it can accept postional arguments.
    * the working directory policy is set with setting: RUNSCRIPT_CHDIR_POLICY

# Static Files
* Linking CSS files: <link rel="stylesheet" href="styles.css">

# Misc
* getting the current working directory:
    import os
    print os.getcwd()

# Waiting to Be Played With
* `default` for a model field with foreign reference (https://docs.djangoproject.com/en/2.0/ref/models/fields/#default)
* How is it possible to use django-model-utils without adding to installed list?
* Template Context Processor?
* What/how of django content type
* Authentication
* how to define get params that must exist?
* drf
* Functions in django.utils.functional (other than cached_property decorator)
* User settings
* Frontend Capabilities
    * hotkeys
    * simplier list navigation
    * change ordering
    * highlight the last updated/created item
  

# Python Cookbook
https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/ch14s08.html

# Fuzzy Logic
* fuzzy logic is the logic that is used to describe fuzziness.
* membership is converted from 0/1 to a range of values [0,1] as membership value.
