from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AUser, Session, EngineSession
from utilities.renderers import alexa_render
import json
from utilities.dictionaries import deep_get
from alexa.engines import Question, EmotionalEngine, MedicalEngine


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


# todo Sequence/Scheduling problem... Each time a request comes, there must be an engine serving
# todo Engine triggering another engine
def next_engine(engine_session: EngineSession):
    if engine_session.name == 'EmotionalEngine':
        return 'MedicalEngine'
    if engine_session.name == 'MedicalEngine':
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
            return JsonResponse(alexa_render(output_speech=text_response, should_session_end=True))

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
            follow_engine = engine_class(alexa_user=alexa_user)
            question = follow_engine.question.asked_question

            e_session = EngineSession(user=alexa_user, name=follow_engine.__class__.__name__, state='continue')
            e_session.data = {'level': "question", 'asked_questions': [question]}
            e_session.save()
            text_response = '{} {}'.format(text_response, question)
    elif engine_session and engine_session.state == 'continue':
        engine_class = globals()[engine_session.name]
        engine = engine_class(alexa_user=alexa_user)
        question = engine.question.asked_question
        text_response = '{} {}'.format(text_response, question)
        engine_session.data['level'] = 'question'
        engine_session.save()
    else:
        engine = MedicalEngine(alexa_user)
        question = engine.question.asked_question
        e_session = EngineSession(user=alexa_user, name=engine.__class__.__name__, state='continue')
        e_session.data = {'level': 'question', 'asked_questions': [question]}
        e_session.save()
        text_response = '{} {}'.format(text_response, question)

    return JsonResponse(alexa_render(output_speech=text_response))
