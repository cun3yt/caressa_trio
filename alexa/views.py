from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AUser, Session, EngineSession
from utilities.renderers import alexa_render
import json
from utilities.dictionaries import deep_get
from alexa.engines import EmotionalEngine, MedicalEngine, WeightEngine, JokeEngine, AdEngine, \
    engine_registration, NewsEngine, TalkBitEngine, EndState, OutroEngine
from icalevents.icalevents import events as query_events
from datetime import datetime, timedelta
from django.shortcuts import render
from utilities.logger import log
from random import sample


def main_view(request):
    return render(request, 'main.html')


class BasicEngineSpawner:
    def __init__(self, a_user: AUser, is_new_session: bool, last_engine_session: EngineSession, request_type,
                 intent_name):
        self.a_user = a_user
        self.is_new_session = is_new_session
        self.last_engine_session = last_engine_session
        self.request_type = request_type
        self.intent_name = intent_name

        self.greeting_engine = 'EmotionalEngine'

        self.timed_engines = [
            'MedicalEngine',
            'WeightEngine',
        ]
        self.notif_engines = [
            'TalkBitEngine',
        ]
        self.filler_engines = [
            'NewsEngine',
            'JokeEngine',
            'AdEngine',
        ]
        self.outro_engine = 'OutroEngine'

    def _get_engine_from_schedule(self):
        alexa_user = self.a_user
        log("get_engine_from_schedule with AUser::{}".format(alexa_user.id))

        schedule = alexa_user.engine_schedule.encode(encoding='UTF-8')
        events = query_events(string_content=schedule,
                              start=datetime.now(),
                              end=(datetime.now() + timedelta(minutes=10)),
                              fix_apple=True)

        engine_name = None

        log("# events fetched from schedule: {}".format(len(events)))

        for event in events:
            log(" >> event in question: {}".format(event.summary))
            if EngineSession.objects.filter(created__range=(event.start, event.end), state='done').count() == 0:
                log("  This is being EXECUTED: {}".format(event.summary))
                engine_name = event.summary
                break
            log(" PASSED...")

        if not engine_name:
            return None

        return engine_name

    def _get_available_timed_engines(self):
        engine_name = self._get_engine_from_schedule()
        return [engine_name]

    def _get_available_notif_engines(self):
        if TalkBitEngine.fetch_user_post(self.a_user.user):
            return ['TalkBitEngine']
        return []

    @staticmethod
    def _random_select(engine_list):
        """
        todo Usage statistics based selection may be better here, stats including last run time of engines
        :param engine_list:
        :return: str
        """
        return sample(engine_list, 1)[0]

    def _select_filler_engine(self):
        """
        todo Usage statistics and user preferences will play role here, stats including last run time of engines
        :return:
        """
        return sample(self.filler_engines, 1)[0]

    def spawn(self):
        if self.is_new_session:
            engine_name = self.greeting_engine
            return get_engine_instance(engine_name, self.a_user)

        available_timed_engines = self._get_available_timed_engines()
        available_notif_engines = self._get_available_notif_engines()

        if len(available_timed_engines) > 0 or len(available_notif_engines) > 0:
            engine_name = self._random_select(available_timed_engines + available_notif_engines)
            return get_engine_instance(engine_name, self.a_user)

        engine_name = self._select_filler_engine()
        engine_name = self.outro_engine if engine_name is None else engine_name

        return get_engine_instance(engine_name, self.a_user)


def get_engine_instance(engine_name, alexa_user: AUser):
    engine_class = globals()[engine_name]
    return engine_class(alexa_user=alexa_user)


class Conversation:
    def __init__(self, request):
        req_body = json.loads(request.body)
        session_id = deep_get(req_body, 'session.sessionId', '')
        user_id = deep_get(req_body, 'context.System.user.userId', '')

        self.alexa_user = AUser.objects.get_or_create(alexa_id=user_id)[0]
        self.engine_session = self.alexa_user.last_engine_session()
        self.sess, self.is_new_session = Session.objects.get_or_create(alexa_id=session_id, alexa_user=self.alexa_user)

        self.req = {
            'type': deep_get(req_body, 'request.type'),
            'intent': deep_get(req_body, 'request.intent'),
            'intent_name': deep_get(req_body, 'request.intent.name'),
        }

        self.spawner = BasicEngineSpawner(self.alexa_user, self.is_new_session, self.engine_session, self.req['type'], self.req['intent_name'])

        log('-----')
        log(" TYPE: {}\n INTENT: {}".format(self.req.get('type'), self.req.get('intent_name')))
        log(" FULL INTENT: {}".format(self.req.get('intent')))
        log("Engine Session? {}\n"
            "Session State: {}\n"
            "Intent: {}".format("Yes" if self.engine_session else "No",
                                self.engine_session.state if self.engine_session else "None",
                                self.req.get('intent_name')))

        self.response = {
            'text': '',
            'should_session_end': False,
        }

    @property
    def is_the_engine_session_going_on(self):
        return self.engine_session and self.engine_session.is_continuing

    @property
    def is_there_an_intent(self):
        return self.req.get('intent') is not None

    @staticmethod
    def continue_engine_session(session: EngineSession, alexa_user: AUser, intent_name, request_intent):
        __level = session.data.get('level')
        engine = get_engine_instance(session.name, alexa_user)

        levels = __level.split('.')

        traverser = engine

        for lev in levels:
            if lev == 'question':
                traverser = traverser.question
            elif lev == 'profile_builder':
                traverser = traverser.profile_builder
            else:
                traverser = traverser.intents.get(lev)

        intent = traverser.intents.get(intent_name)

        if intent.process_fn:
            intent.process_fn(intent=request_intent)

        return intent.get_random_response(), intent

    def _wire_brain_connections_post_intent(self, engine_intent_object):
        if engine_intent_object.engine_session:         # todo is this if/else necessary??
            # if the intent has specific direction on engine session it takes precedence
            self.engine_session.state = engine_intent_object.engine_session
        else:
            if engine_intent_object.is_end_state():
                self.engine_session.set_state_done()
            else:
                self.engine_session.set_state_continue()

        if engine_intent_object.end_session:  # end the alexa session
            self.engine_session.set_state_continue(start_level='question')
            self.engine_session.save()
            self.response['should_session_end'] = True
            return

        # "profile builder execution" if the user don't have it in her profile.
        if engine_intent_object.profile_builder and (self.alexa_user.profile_get(engine_intent_object.profile_builder.key) is None):
            self.engine_session.set_state_continue(
                additional_level='{intent}.profile_builder'.format(intent=self.req.get('intent_name')),
                asked_question=engine_intent_object.profile_builder.asked_question
            )
            self.engine_session.save()
            self.response['text'] = '{} {}'.format(self.response['text'],
                                                   engine_intent_object.profile_builder.asked_question)

        elif not engine_intent_object.is_end_state():
            self.engine_session.set_state_continue(
                additional_level='{intent}.question'.format(intent=self.req.get('intent_name')),
                asked_question=engine_intent_object.question.asked_question
            )
            self.engine_session.save()
            self.response['text'] = '{} {}'.format(self.response['text'],
                                                   engine_intent_object.question.asked_question)

        else:
            self.engine_session.set_state_done(additional_level='{intent}'.format(intent=self.req.get('intent_name')))
            self.engine_session.save()
            follow_engine = self.spawner.spawn()

            if isinstance(follow_engine, OutroEngine):
                closing = follow_engine.get_random_closing()
                e_session = EngineSession(user=self.alexa_user,
                                          name=follow_engine.__class__.__name__,
                                          state='done')
                e_session.data = {'closing': closing}
                e_session.save()
                self.response['text'] = '{}. By the way {}'.format(self.response['text'], closing)
                self.response['should_session_end'] = True
                return

            question = follow_engine.question.asked_question

            e_session = EngineSession(user=self.alexa_user,
                                      name=follow_engine.__class__.__name__,
                                      state='continue')
            e_session.data = {'level': "question", 'asked_questions': [question]}
            e_session.save()
            self.response['text'] = '{} {}'.format(self.response['text'], question)

    def run(self):
        self.response['text'] = 'Welcome, ' if self.req['type'] == 'LaunchRequest' else ''

        if self.req['type'] == 'SessionEndedRequest':
            log("~~~ Session ended request came ~~~")
            return JsonResponse(alexa_render(speech='OK, thanks for using Caressa'))

        log("START: ")

        if self.is_the_engine_session_going_on and self.is_there_an_intent:
            log(" Continuing Engine Session and there is an INTENT")
            response, engine_intent_object = self.continue_engine_session(self.engine_session,
                                                                          self.alexa_user,
                                                                          self.req.get('intent_name'),
                                                                          self.req.get('intent'))
            self.response['text'] = "{}{}".format(self.response['text'], response)

            self._wire_brain_connections_post_intent(engine_intent_object)

        elif self.is_the_engine_session_going_on:
            log(" Continuing Engine Session and there is NO intent")
            engine = get_engine_instance(self.engine_session.name, self.alexa_user)
            question = engine.question.asked_question
            self.response['text'] = '{} {}'.format(self.response['text'], question)
            self.engine_session.set_state_continue(start_level='question')
            self.engine_session.save()

        else:
            log(" No continuing engine session (must be 'open caressa')")
            engine = self.spawner.spawn()
            question = engine.question.asked_question
            e_session = EngineSession(user=self.alexa_user, name=engine.__class__.__name__, state='continue')
            e_session.data = {'level': 'question', 'asked_questions': [question]}
            e_session.save()
            self.response['text'] = '{} {}'.format(self.response['text'], question)
            log(" Response: {}".format(self.response['text']))


# todo 1. Engine triggering another engine
# todo 2. Value (slot) confirmation
@csrf_exempt
def alexa_io(request):
    conversation = Conversation(request)
    conversation.run()
    text_response = conversation.response['text']
    return JsonResponse(alexa_render(speech=text_response,
                                     should_session_end=conversation.response.get('should_session_end')))
