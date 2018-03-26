from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AUser, Session, EngineSession
from utilities.dictionaries import deep_get
from utilities.renderers import alexa_render
import json
from random import sample


# question => expected answers ("intent"s) => {collect data} and text & where to go next...

class Question:
    def __init__(self, versions, intent_list, reprompt=None):
        self.versions = versions
        self.reprompt = reprompt
        self.intents = {intent.intent_identifier(): intent for intent in intent_list}
        self.asked_question = self._get_random_version()

    def _get_random_version(self):
        return sample(self.versions, 1)[0]


class Intent:
    def __init__(self, name, response_set, slots=None, follow_engine=None, samples=None, process_fn=None,
                 question=None):
        self.name = name
        self.response_set = response_set
        self.slots = slots
        self.follow_engine = follow_engine
        self.samples = samples
        self.process_fn = process_fn
        self.question = question

    @classmethod
    def intent_identifier(cls):
        return "intent-identifier"

    def is_end_state(self):         # is leaf?
        return not self.question

    def get_random_response(self):
        return sample(self.response_set, 1)[0]

    def render(self, render_type='json'):
        pass


class SlotTypeValue:
    def __init__(self, value, synonyms=None):
        self.value = value
        self.synonyms = synonyms

    def render(self, render_type='json'):
        dict_repr = {
            "name": {
                "value": self.value
            }
        }

        if self.synonyms:
            dict_repr['synonyms'] = self.synonyms

        return json.dumps(dict_repr) if render_type == 'json' else dict_repr


class SlotType:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def render(self, render_type='json'):
        dict_repr = {
            "name": self.name,
            "values": [value.render(render_type='dict') for value in self.values],
        }
        return json.dumps(dict_repr) if render_type == 'json' else dict_repr


class Slot:
    def __init__(self, name, slot_type: SlotType):
        self.name = name
        self.slot_type = slot_type

    def render(self, render_type='json'):
        dict_repr = {
            "name": self.name,
            "type": self.slot_type.name
        }
        return json.dumps(dict_repr) if render_type == 'json' else dict_repr


class GoodIntent(Intent):
    def __init__(self, slots=None, process_fn=None, question=None):
        name = GoodIntent.intent_identifier()
        response_set = [
            "that's good to hear.",
            "that's awesome!",
        ]
        samples = [
            "I feel {feeling_good_slot}",
            "I am feeling {feeling_good_slot}",
            "great",
            "the best",
            "good",
        ]
        super(GoodIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                         process_fn=process_fn, question=question)

    def get_random_response(self):
        return sample(self.response_set, 1)[0]

    @classmethod
    def intent_identifier(cls):
        return 'good_intent'


class BadIntent(Intent):
    @classmethod
    def intent_identifier(cls):
        return 'bad_intent'

    def __init__(self, slots=None, process_fn=None, question=None):
        name = self.intent_identifier()
        response_set = [
            "I am sorry to hear.",
            "Ah, that's bad!",
            "Oh, I'm sorry",
        ]
        samples = [
            "I am feeling {feeling_bad_slot}",
            "I feel {feeling_bad_slot}",
            "sad",
            "terrible",
            "worse",
            "bad",
        ]
        super(BadIntent, self).__init__(name=name, response_set=response_set, samples=samples, slots=slots,
                                         process_fn=process_fn, question=question)


class Engine:
    def __init__(self, question: Question):
        self.question = question

    def render(self, render_type='json'):
        pass


class EmotionalEngine(Engine):
    def __init__(self):
        init_question = Question(
            versions=["How are you?",
                      "How are you today?",
                      ],
            reprompt=["How do you feel?",
                      ],
            intent_list=[
                GoodIntent(question=Question(versions=['so is it good?'],
                                             intent_list=[GoodIntent()])),
                BadIntent()
            ],
        )

        super(EmotionalEngine, self).__init__(question=init_question)


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
    __level = session.data.get('level')
    engine_class = globals()[session.name]
    engine = engine_class()

    levels = __level.split('.')

    traverser = engine

    for lev in levels:
        traverser = traverser.question if lev == 'question' else traverser.intents.get(lev)

    intent = traverser.intents.get(intent_name)
    return intent.get_random_response(), intent


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
    req_intent = deep_get(req_body, 'request.intent')
    intent_name = deep_get(req_body, 'request.intent.name')

    text_response = 'Welcome, ' if req_type == 'LaunchRequest' else ''

    if req_type == 'SessionEndedRequest':
        print("~~~ Session ended request came ~~~")
        return JsonResponse(alexa_render(output_speech='OK'))

    print('-----')
    print(" TYPE: {}\n INTENT: {}".format(req_type, intent_name))
    print(" FULL INTENT: {}".format(req_intent))
    print(
        "Engine Session? {}\nSession State: {}\nIntent: {}".format("Yes" if engine_session else "No",
                                                                   engine_session.state if engine_session else "None",
                                                                   intent_name))

    if engine_session and engine_session.state == 'continue' and req_intent:
        response, intent = continue_engine_session(engine_session, intent_name)
        text_response = "{}{}".format(text_response, response)

        engine_session.state = 'done' if intent.is_end_state() else 'continue'

        if not intent.is_end_state():
            engine_session.data['level'] = '{level}.{intent_name}.question'.format(level=engine_session.data['level'],
                                                                                   intent_name=intent_name)
            engine_session.data['asked_questions'].append(intent.question.asked_question)
            engine_session.save()
            text_response = '{} {}'.format(text_response, intent.question.asked_question)

        else:
            engine_session.data['level'] = '{level}.{intent_name}'.format(level=engine_session.data['level'],
                                                                          intent_name=intent_name)
            engine_session.save()
            engine_name = next_engine(engine_session)
            engine_class = globals()[engine_name]
            follow_engine = engine_class()
            question = follow_engine.question.asked_question

            e_session = EngineSession(user=alexa_user, name=follow_engine.__class__.__name__, state='continue')
            e_session.data = {'level': "question", 'asked_questions': [question]}
            e_session.save()
            text_response = '{} {}'.format(text_response, question)
    elif engine_session and engine_session.state == 'continue':
        engine_class = globals()[engine_session.name]
        engine = engine_class()
        question = engine.question.asked_question
        text_response = '{} {}'.format(text_response, question)
    else:
        engine = EmotionalEngine()
        question = engine.question.asked_question
        e_session = EngineSession(user=alexa_user, name=engine.__class__.__name__, state='continue')
        e_session.data = {'level': 'question', 'asked_questions': [question]}
        e_session.save()
        text_response = '{} {}'.format(text_response, question)

    return JsonResponse(alexa_render(output_speech=text_response))
