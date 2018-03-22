from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AUser, Request, Session, EngineSession
from utilities.dictionaries import deep_get
from utilities.renderers import alexa_render
import json


tasks = {
    'EmotionEngine': {'name': 'EmotionEngine'},
    'MedicalEngine': {'name': 'MedicalEngine'},
    'DailyMoodEngine': {'name': 'DailyMoodEngine'},
}


# question => expected answers ("intent"s) => {collect data} and text & where to go next...


class EmotionalEngine:
    def __init__(self):
        self.start_question = "how-are-you"
        self.questions = {
            "how-are-you": {
                "question": [
                    "How are you?",
                    "How are you today?",
                    "How do you feel?"
                ],
                "intents-expected": {
                    "good_intent": {
                        "follow-up": {
                            "text": [
                                "that's good to hear.",
                            ]
                        }
                    },
                    "bad_intent": {
                        "follow-up": {
                            "text": [
                                "I am sorry to hear that.",
                            ],
                            "follow-engine": "DailyMoodEngine",
                        }
                    },
                    "neutral_intent": {
                        "follow-up": {
                            "text": [
                                "Alright.",
                            ],
                        }
                    }
                }
            }
        }


class DailyMoodEngine:
    def __init__(self):
        self.start_question = "like-to-hear-a-joke"
        self.questions = {
            "like-to-hear-a-joke": {
                "question": [
                    "Would you like to hear a joke?"
                ],
                "intents-expected": {
                    "yes_intent": {
                        "follow-up": {
                            "text": [
                                "Why are bikes always slow? Because they are two tired!"
                            ]
                        }
                    },
                    "no_intent": {
                        "follow-up": {
                            "text": [
                                "No problem."
                            ]
                        }
                    }
                }
            }
        }


class MedicalEngine:
    def __init__(self):
        self.start_question = "blood-pressure"
        self.questions = {
            "blood-pressure": {
                "question": [
                    "Did you measure your blood pressure?",
                ],
                "intents-expected": {
                    "yes_intent": {
                        "follow-up": {
                            "text": [
                                "Atta girl!",
                                "Good for you little punk! SO WHAT?"
                            ]
                        }
                    },
                    "no_intent": {
                        "follow-up": {
                            "text": [
                                "Go fun yourself then..."
                            ]
                        }
                    }
                }
            }
        }


def continue_engine_session(session: EngineSession, intent_name):
    level = session.data.get('level')
    engine_class = globals()[session.name]
    engine = engine_class()
    intent_response = deep_get(engine.questions, "{}.{}".format(level, intent_name))
    return deep_get(intent_response, 'follow-up.text')[0]


def next_engine(engine_session: EngineSession):
    if engine_session.name == 'EmotionalEngine':
        return 'MedicalEngine'
    if engine_session.name == 'MedicalEngine':
        return 'DailyMoodEngine'
    if engine_session.name == 'DailyMoodEngine':
        return 'EmotionalEngine'


@csrf_exempt
def alexa_io(request):
    req_body = json.loads(request.body)

    session_id = deep_get(req_body, 'session.sessionId', '')
    user_id = deep_get(req_body, 'context.System.user.userId', '')

    alexa_user = AUser.objects.get_or_create(alexa_id=user_id)[0]
    engine_session = alexa_user.last_engine_session()

    sess, is_new_session = Session.objects.get_or_create(alexa_id=session_id, alexa_user=alexa_user)
    # alexa_req = Request.objects.create(session=sess, request=req_body)

    req_type = deep_get(req_body, 'request.type')
    intent = deep_get(req_body, 'request.intent')
    intent_name = deep_get(req_body, 'request.intent.name')

    print('-----')
    print(" TYPE: {}\n INTENT: {}".format(req_type, intent_name))
    print(" FULL INTENT: {}".format(intent))

    text_response = 'Welcome, ' if req_type == 'LaunchRequest' else ''

    print(
        "Engine Session? {}\nSession State: {}\nIntent: {}".format("Yes" if engine_session else "No",
                                                                   engine_session.state if engine_session else "None",
                                                                   intent_name))

    if engine_session and engine_session.state == 'continue' and intent:
        response = continue_engine_session(engine_session, intent_name)
        text_response = "{}{}".format(text_response, response)
        engine_session.state = 'done'
        engine_session.save()

        engine_name = next_engine(engine_session)
        engine_class = globals()[engine_name]
        engine = engine_class()
        start_question = engine.questions[engine.start_question]

        e_session = EngineSession(user=alexa_user, name=engine_name, state='continue')
        e_session.data = {'level': "{}.intents-expected".format(engine.start_question)}
        e_session.save()
        question = start_question['question'][0]
        text_response = '{} {}'.format(text_response, question)
    elif engine_session and engine_session.state == 'continue':
        engine_class = globals()[engine_session.name]
        engine = engine_class()
        question = engine.questions[engine.start_question]['question'][0]
        text_response = '{} {}'.format(text_response, question)
    else:
        engine = EmotionalEngine()
        question = engine.questions[engine.start_question]['question'][0]
        e_session = EngineSession(user=alexa_user, name='EmotionalEngine', state='continue')
        e_session.data = {'level': '{}.intents-expected'.format(engine.start_question)}
        e_session.save()
        text_response = '{} {}'.format(text_response, question)

    return JsonResponse(alexa_render(output_speech=text_response))
