from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AUser, Session, EngineSession
from utilities.renderers import alexa_render
import json
from utilities.dictionaries import deep_get
from alexa.engines import Question, EmotionalEngine, MedicalEngine, JokeEngine, AdEngine, engine_registration
from icalevents.icalevents import events as query_events
from datetime import datetime, timedelta
import logging
import daiquiri


# 1. Planning td items for a user:
# A: set of { td-interval (start-end), repetition-schedule, engine, priority }
# this will be combined with engine-session data
# B: engine sessions data

# 2. what about scheduling the postponed td items?
# postpone types:
# A. next session: already covered with 'continue' engine-session type
# B. for specified amount of time...

daiquiri.setup(level=logging.INFO)
logger = daiquiri.getLogger()


def get_engine_from_cascade(alexa_user: AUser):
    engine = get_engine_from_schedule(alexa_user)
    if engine:
        return engine

    engine = get_engine_from_critical_list(alexa_user)

    if engine:
        return engine

    return get_engine_from_filler(alexa_user)


def get_engine_from_schedule(alexa_user: AUser):
    logger.info("get_engine_from_schedule with AUser::{}".format(alexa_user.id))

    schedule = alexa_user.engine_schedule.encode(encoding='UTF-8')
    logger.info(datetime.now())
    logger.info(datetime.now() + timedelta(minutes=10))
    events = query_events(string_content=schedule, start=datetime.now(), end=(datetime.now() + timedelta(minutes=10)), fix_apple=True)

    # filler or info-collector engines will come here..
    # engine_name = 'EmotionalEngine'
    engine_name = None

    logger.info("# events fetched from schedule: {}".format(len(events)))

    for event in events:
        logger.info(" >> event in question: {}".format(event.summary))
        if EngineSession.objects.filter(created__range=(event.start, event.end), state='done').count() == 0:
            logger.info("  This is being EXECUTED: {}".format(event.summary))
            engine_name = event.summary
            break
        logger.info(" PASSED...")

    if not engine_name:
        return None

    engine_class = globals()[engine_name]
    return engine_class(alexa_user=alexa_user)


def get_engine_from_critical_list(alexa_user: AUser):
    logger.info("get_engine_from_critical_list for AUser: {}".format(alexa_user.id))
    return None


def get_engine_from_filler(alexa_user: AUser):
    logger.info('get_engine_from_filler for AUser: {}'.format(alexa_user.id))
    return None


def continue_engine_session(session: EngineSession, alexa_user: AUser, intent_name, request_intent):
    __level = session.data.get('level')
    engine_class = globals()[session.name]
    engine = engine_class(alexa_user=alexa_user)

    levels = __level.split('.')

    traverser = engine

    for lev in levels:
        traverser = traverser.question if lev == 'question' else traverser.intents.get(lev)

    intent = traverser.intents.get(intent_name)

    if intent.process_fn:
        intent.process_fn(intent=request_intent)

    return intent.get_random_response(), intent


# todo 2. Engine triggering another engine
# todo 3. Value (slot) confirmation
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
        logger.info("~~~ Session ended request came ~~~")
        return JsonResponse(alexa_render(speech='OK'))

    logger.info('-----')
    logger.info(" TYPE: {}\n INTENT: {}".format(req_type, intent_name))
    logger.info(" FULL INTENT: {}".format(req_intent))
    logger.info(
        "Engine Session? {}\nSession State: {}\nIntent: {}".format("Yes" if engine_session else "No",
                                                                   engine_session.state if engine_session else "None",
                                                                   intent_name))

    logger.info("START: ")
    if engine_session and engine_session.state == 'continue' and req_intent:
        logger.info(" Continuing Engine Session and there is an INTENT")
        response, intent = continue_engine_session(engine_session, alexa_user, intent_name, req_intent)
        text_response = "{}{}".format(text_response, response)

        if intent.engine_session:
            # if the intent has specific direction on engine session it takes precedence
            engine_session.state = intent.engine_session
        else:
            engine_session.state = 'done' if intent.is_end_state() else 'continue'

        if intent.end_session:  # end the alexa session
            engine_session.data['level'] = 'question'   # start over in the next session
            engine_session.save()
            return JsonResponse(alexa_render(speech=text_response, should_session_end=True))

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
            follow_engine = get_engine_from_schedule(alexa_user=alexa_user)
            question = follow_engine.question.asked_question

            e_session = EngineSession(user=alexa_user, name=follow_engine.__class__.__name__, state='continue')
            e_session.data = {'level': "question", 'asked_questions': [question]}
            e_session.save()
            text_response = '{} {}'.format(text_response, question)
    elif engine_session and engine_session.state == 'continue':
        logger.info(" Continuing Engine Session and there is NO intent")
        engine_class = globals()[engine_session.name]
        engine = engine_class(alexa_user=alexa_user)
        question = engine.question.asked_question
        text_response = '{} {}'.format(text_response, question)
        engine_session.data['level'] = 'question'
        engine_session.save()
    else:
        logger.info(" No continuing engine session (must be 'open caressa')")
        engine = get_engine_from_schedule(alexa_user)
        question = engine.question.asked_question
        e_session = EngineSession(user=alexa_user, name=engine.__class__.__name__, state='continue')
        e_session.data = {'level': 'question', 'asked_questions': [question]}
        e_session.save()
        text_response = '{} {}'.format(text_response, question)

    return JsonResponse(alexa_render(speech=text_response))
