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



# Sorular

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