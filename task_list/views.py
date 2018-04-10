from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AlexaUser, AlexaSession, AlexaRequest
from utilities.dictionaries import deep_get
from utilities.renderers import alexa_render
import json


def main_view(request):
    return render(request, 'main.html')


class ConversationEngineMixin:
    def __init__(self):
        self.intents = {}   # intent mapping
        self.intersession_continuity = False
        self.default_text = 'I am Caressa and I don\'t have any idea what the hell am doing?!'


class GreetingEngine(ConversationEngineMixin):
    def __init__(self):
        super(GreetingEngine, self).__init__()

    def run(self):
        directive = {
            'intent_name': 'ci_current_feeling',
            'slot_to_elicit': 'ci_feeling',     # todo: needs to be `cs_feeling`
        }
        return alexa_render(speech='Hi, how are you?', directive=directive)


class MedicalEngine(ConversationEngineMixin):
    def __init__(self):
        super(MedicalEngine, self).__init__()

    def run(self):
        return alexa_render(speech='This is medical engine!')


class SocialEngine(ConversationEngineMixin):
    def __init__(self):
        super(SocialEngine, self).__init__()

    def run(self):
        return alexa_render(speech='This is social engine!')


registered_engines = [
    {
        'name': 'GreetingEngine',
        'priority': 100,            # higher the priority, more important the skill
        'interval': 4*60*60,        # every 4 hours
    },
    {
        'name': 'MedicalEngine',
        'priority': 80,
        'interval': 6*60*60,
    },
    {
        'name': 'SocialEngine',
        'priority': 60,
        'interval': 1*60*60,
    },
]


def fetch_from_state(alexa_user: AlexaUser, sess: AlexaSession, alexa_req: AlexaRequest):
    return 'GreetingEngine'


def brain_run(alexa_user, sess, alexa_req):
    req_body = alexa_req.request
    req_type = deep_get(req_body, 'request.type')

    print(" TYPE: {}, INTENT: {}".format(req_type, deep_get(req_body, 'request.intent.name')))

    if req_type == 'LaunchRequest':
        engine_name = fetch_from_state(alexa_user, sess, alexa_req)
        engine = globals()[engine_name]
        return engine().run()

    if req_type == 'SessionEndedRequest':
        return alexa_render('see you later!')

    intent = deep_get(req_body, 'request.intent')

    text = 'I am Caressa and I don\'t have any idea what I am doing?!'

    try:
        print(intent)

        intent_name = deep_get(intent, 'name') if intent else 'none'

        print('intent name: {}'.format(intent_name))

        if intent and intent_name == 'ci_set_value':
            val_to_set = deep_get(intent, 'slots.value.value')
            sess.number = int(val_to_set)
            sess.save()
            text = 'Your value is set to {}.'.format(val_to_set)

        if intent and intent_name == 'ci_get_value':
            text = 'Your value is {}.'.format(sess.number)

        if intent and intent_name == 'ci_my_feeling':
            directive = {
                'intent_name': 'ci_my_feeling',
                'slot_to_elicit': 'feeling',
            }
            return alexa_render(speech='How do you feel?', directive=directive)

    except Exception:
        print("Exception happened! ")

    return alexa_render(speech=text)


@csrf_exempt
def alexa_broker(request):
    req_body = json.loads(request.body)

    print('-----')

    session_id = deep_get(req_body, 'session.sessionId', '')
    user_id = deep_get(req_body, 'context.System.user.userId', '')

    alexa_user = AlexaUser.objects.get_or_create(alexa_id=user_id)[0]
    sess = AlexaSession.objects.get_or_create(alexa_id=session_id, alexa_user=alexa_user)[0]
    alexa_req = AlexaRequest.objects.create(session=sess, request=req_body)

    text_response = brain_run(alexa_user, sess, alexa_req)

    return JsonResponse(text_response)
