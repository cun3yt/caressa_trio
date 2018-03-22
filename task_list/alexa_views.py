from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AlexaUser, AlexaSession, AlexaRequest
from utilities.dictionaries import deep_get
from utilities.renderers import alexa_render
import json


class ConversationEngineMixin:
    def __init__(self):
        self.intents = {}   # intent mapping
        self.intersession_continuity = False
        self.default_text = 'I am Caressa and I don\'t have any idea what the hell am doing?!'


class EmotionEngine(ConversationEngineMixin):
    def __init__(self):
        super(EmotionEngine, self).__init__()
        self.default_text = 'I am Emotional Engine'

    def run(self):
        pass


class MedicalEngine(ConversationEngineMixin):
    def __init__(self):
        super(MedicalEngine, self).__init__()
        self.default_text = 'I am Medical Engine'

    def run(self):
        pass

        # directive = {
        #     'intent_name': 'ci_current_feeling',
        #     'slot_to_elicit': 'ci_feeling',     # todo: needs to be `cs_feeling`
        # }
        # return alexa_render(output_speech='Hi, how are you?', directive=directive)


class Conversation:
    def __init__(self):
        self.engine = None


tasks_to_do = [
    {
        "engine": 'EmotionalEngine',
        "period": '',
    },
    {
        "engine": 'MedicalEngine',
        "period": '',
    }
]


@csrf_exempt
def alexa_broker_good_luck(request):
    req_body = json.loads(request.body)

    session_id = deep_get(req_body, 'session.sessionId', '')
    user_id = deep_get(req_body, 'context.System.user.userId', '')

    alexa_user = AlexaUser.objects.get_or_create(alexa_id=user_id)[0]

    last_request = alexa_user.get_last_request()

    sess, is_new_session = AlexaSession.objects.get_or_create(alexa_id=session_id, alexa_user=alexa_user)[0]
    alexa_req = AlexaRequest.objects.create(session=sess, request=req_body)

    req_type = deep_get(req_body, 'request.type')
    intent = deep_get(req_body, 'request.intent')
    intent_name = deep_get(req_body, 'request.intent.name')

    print('-----')
    print(" TYPE: {}\n INTENT: {}".format(req_type, intent_name))
    print(" FULL INTENT: {}".format(intent))

    text_response = 'Welcome, ' if req_type == 'LaunchRequest' else ''
    text_response += "say something like 'yep', 'of course not' or 'I feel good'"

    return JsonResponse(alexa_render(output_speech=text_response))
