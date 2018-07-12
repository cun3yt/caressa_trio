from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince as djtimesince
from django.utils import timezone
from datetime import timedelta, datetime
from random import sample
import pytz
from alexa.models import AUser, Joke, News, User
from alexa.intents import GoodIntent, BadIntent, YesIntent, NoIntent, BloodPressureIntent, WeightIntent
from actions.models import UserAction, UserPost, UserListened
from utilities.dictionaries import deep_get
from caressa.settings import CONVERSATION_ENGINES


class Question:
    def __init__(self, versions=None, intent_list=None, reprompt=None):
        self.versions = versions
        self.reprompt = reprompt  # todo Reprompt can be built based on what is available in intent_list!!
        self.intents = {intent.intent_identifier(): intent for intent in intent_list}
        self.asked_question = self._get_random_version()

    def _get_random_version(self):
        if self.versions is None:
            return ''

        return sample(self.versions, 1)[0]


class Engine:
    default_ttl = CONVERSATION_ENGINES['ttl']     # time to live is 10 minutes by default

    def __init__(self, question: Question, alexa_user: AUser, engine_session=None,
                 ttl=None):
        self.question = question
        self.alexa_user = alexa_user
        self.ttl = Engine.default_ttl if ttl is None else ttl
        self.engine_session = engine_session

    def render(self, render_type='json'):
        pass


class EmotionalEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=["How are you?",
                      "How are you today?",
                      ],
            reprompt=["How do you feel?",
                      ],
            intent_list=[
                GoodIntent(
                    process_fn=self.update_on_good_intent
                ),
                BadIntent(
                    process_fn=self.update_on_bad_intent
                )
            ],
        )

        super(EmotionalEngine, self).__init__(question=init_question,
                                              alexa_user=alexa_user,
                                              ttl=30, **kwargs)

    def update_on_good_intent(self, **kwargs):
        self.alexa_user.update_emotion('happiness', percentage=0.1, max_value=75)
        print(" >>> update_on_good_intent is called")

    def update_on_bad_intent(self, **kwargs):
        self.alexa_user.update_emotion('happiness', percentage=-5.0)
        print(" >>> update_on_bad_intent is called")


class ProfileBuilderForJoke(Question):
    def __init__(self, alexa_user: AUser):
        self.key = 'joke'
        self.alexa_user = alexa_user
        versions = ['Do you like such jokes?', ]
        reprompt = ["Sorry, I didn't get it. Do you like such jokes? Yes or No?", ]
        intents = [
            YesIntent(response_set=['OK, I will tell more of them as comes to my mind'], process_fn=self.save_yes),
            NoIntent(response_set=['No problem, I know my jokes are a bit lame'], process_fn=self.save_no),
        ]
        super(ProfileBuilderForJoke, self).__init__(versions=versions, intent_list=intents, reprompt=reprompt)

    def save_yes(self, **kwargs):
        self.alexa_user.profile_set('joke', True)

    def save_no(self, **kwargs):
        self.alexa_user.profile_set('joke', False)


class JokeEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=['Would you like to hear a joke?', ],
            reprompt=["Do you want a joke?", ],
            intent_list=[
                YesIntent(
                    response_set=self._get_joke_and_render,
                    question=Question(versions=['Was it funny?',
                                                'Did you like this joke?', ],
                                      intent_list=[
                                          YesIntent(
                                              response_set=['Thanks!'],
                                              process_fn=self._save_joke_like),
                                          NoIntent(response_set=['OK']),
                                      ]),
                    # profile_builder=ProfileBuilderForJoke(alexa_user=alexa_user),
                ),
                NoIntent(response_set=['No problem', ])
            ]
        )

        super(JokeEngine, self).__init__(question=init_question, alexa_user=alexa_user, ttl=1*60, **kwargs)

    def _get_joke(self):
        if self.engine_session and self.engine_session.get_target_object_id():
            joke_id = self.engine_session.get_target_object_id()
            joke = Joke.objects.get(id=joke_id)
            return joke

        joke = Joke.fetch_random()

        if self.engine_session:
            self.engine_session.set_target_object_id(joke.id)

        return joke

    def _get_joke_and_render(self):
        joke = self._get_joke()
        return '{main}<break time="1s"/>{punchline}'.format(main=joke.main, punchline=joke.punchline)

    def _save_joke_like(self, **kwargs):
        from alexa.models import UserActOnContent
        joke = self._get_joke()
        act = UserActOnContent(user=self.alexa_user.user,
                               verb='laughed at',
                               object=joke)
        act.save()


class NewsEngine(Engine):
    """
    todo consider dropping some functions by generalizing with the other similar engines.
    """
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=['Would you like to hear latest news?', ],  # todo should end headline
            reprompt=['Do you want to listen recent news?', ],
            intent_list=[
                YesIntent(
                    response_set=self._get_obj_and_render,
                    question=Question(versions=['Did you like this news?', ],
                                      intent_list=[
                                          YesIntent(
                                              response_set=['Thanks!'],
                                              process_fn=self._save_obj_like),
                                          NoIntent(response_set=['OK']),
                                      ]),
                ),
                NoIntent(response_set=['Maybe later!', ])
            ]
        )

        super(NewsEngine, self).__init__(question=init_question, alexa_user=alexa_user, ttl=1*60, **kwargs)

    def _get_obj(self):
        if self.engine_session and self.engine_session.get_target_object_id():
            obj_id = self.engine_session.get_target_object_id()
            obj = News.objects.get(id=obj_id)
            return obj

        obj = News.fetch_random()

        if self.engine_session:
            self.engine_session.set_target_object_id(obj.id)

        return obj

    def _get_obj_and_render(self):
        obj = self._get_obj()
        return '{headline}<break time="1s"/>{content}'.format(headline=obj.headline, content=obj.content)

    def _save_obj_like(self, **kwargs):
        from alexa.models import UserActOnContent
        obj = self._get_obj()
        act = UserActOnContent(user=self.alexa_user.user,
                               verb='found interesting',
                               object=obj)
        act.save()


class MedicalEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=[
                "Have you taken your blood pressure measurement for the day?",
                "Did you take your blood pressure today?",
            ],
            reprompt=["Have you taken your blood pressure measurements? Yes or no?"],
            intent_list=[
                YesIntent(question=Question(versions=['What are your measurements?'],
                                            reprompt=[
                                                'Please tell me with systolic over diastolic such as 120 over 80'],
                                            intent_list=[
                                                BloodPressureIntent(process_fn=self.save_blood_pressure)
                                            ])),
                NoIntent(question=Question(versions=['Would you like to take your measurement now then come back to '
                                                     'tell it to me?'],
                                           reprompt=["Sorry, I didn't get it. Do you want to measure now and then tell "
                                                     "it to me? Yes or No?"],
                                           intent_list=[
                                               YesIntent(response_set=['You can say Alexa open Caressa after '
                                                                       'you have taken your blood pressure. Bye.'],
                                                         end_session=True,
                                                         engine_session='continue'
                                                         # todo reference back to the previous questions is needed??
                                                         ),
                                               NoIntent(response_set=['Ok, let’s check your blood pressure later.']),
                                           ])),
            ],
        )

        super(MedicalEngine, self).__init__(question=init_question, alexa_user=alexa_user, ttl=15*60, **kwargs)

    def save_blood_pressure(self, **kwargs):
        self.alexa_user.set_medical_state('blood_pressure', {
            'diastolic': deep_get(kwargs, 'intent.slots.diastolic_slot.value'),
            'systolic': deep_get(kwargs, 'intent.slots.systolic_slot.value'),
            'all_params': kwargs,
        })


class WeightEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=[
                "Have you taken your weight measurement for the week?",
                "Did you take your weight measurement this week?",
            ],
            reprompt=["Have you taken your weight measurement yet? Yes or no?", ],
            intent_list=[
                YesIntent(question=Question(versions=['Good. What is your weight in pounds?'],
                                            reprompt=['Please, tell me your weight in pounds, '
                                                      'for example a hundred and twenty pounds.', ],
                                            intent_list=[
                                                WeightIntent(process_fn=self.save_weight),
                                            ])),
                NoIntent(question=Question(versions=['Would you like to go take your weight measurement now, '
                                                     'then come back to let me know?'],
                                           reprompt=["Sorry, I didn't get it. Do you want to measure your weight now "
                                                     "and then tell it to me? Yes or No?"],
                                           intent_list=[
                                               YesIntent(response_set=['You can say Alexa open Caressa '
                                                                       'after you have taken your weight. Goodbye.'],
                                                         end_session=True,
                                                         engine_session='continue'),
                                               NoIntent(response_set=["OK, let's check your blood pressure later."]),
                                           ])),
            ],
        )

        super(WeightEngine, self).__init__(question=init_question, alexa_user=alexa_user, **kwargs)

    def save_weight(self, **kwargs):
        self.alexa_user.set_medical_state('weight', {
            'amount': deep_get(kwargs, 'intent.slots.weight_slot.value'),
            'unit': 'pound',
            'all_params': kwargs,
        })


class AdEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        init_question = Question(
            versions=[
                "So, many seniors suffer from night-time leg cramps. Have you had one recently?",
            ],
            reprompt=["Sorry, I didn't hear you. Did you have any night-time leg cramps lately?"],
            intent_list=[
                YesIntent(question=Question(
                    versions=[
                        "Most leg cramps go away on their own, but sometimes "
                        "they may be linked to an underlying disorder. "
                        "Is your leg cramp so severe, causing you to lose sleep?",
                        ],
                    reprompt=['Is your leg cramp severe?', ],
                    intent_list=[
                        YesIntent(
                            question=Question(
                                versions=[
                                    "A chiropractor can ease the pain with warm massage. "
                                    "Dr. Smith in San Jose has over 20 years experiences. "
                                    "Would you like him to give you a call?",
                                ],
                                reprompt=['Would you like a call from Dr. Smith?', ],
                                intent_list=[
                                    YesIntent(response_set=["Great, I will ask him to give you a call.", ]),
                                    NoIntent(response_set=['That would be fine. Stretching may help relieve '
                                                           'cramp and also prevent future episodes, if they '
                                                           'are done two or three times a day. Hope you will '
                                                           'feel better', ]),
                                ]
                            ),
                        ),
                        NoIntent(response_set=['It is good to hear that it is not severe. '
                                               'Just a friendly reminder: Magnesium is the mineral curing cramps.', ])
                    ]
                )),
                NoIntent(response_set=["It is great to hear that you don't have leg cramps. "
                                       "A little exercise before bed time always helps", ])

            ]
        )
        super(AdEngine, self).__init__(question=init_question, alexa_user=alexa_user, **kwargs)


class TalkBitEngine(Engine):
    """
    Talking about somebody's user post
    The model class for the user post is "UserPost"
    """
    def __init__(self, alexa_user: AUser, **kwargs):
        user = alexa_user.user
        self.user_action = self.fetch_user_post(user)
        user_post = self.user_action.action_object

        time_past = djtimesince(user_post.created, timezone.now())\
            .encode('utf8').replace(b'\xc2\xa0', b' ').decode('utf8')

        statement = '{username} said this {time} ago:<break time="1s"/> {post_content}. Isn\'t it cool?'\
            .format(username=user_post.user.username,
                    time=time_past,
                    post_content=user_post)

        init_question = Question(
            versions=[statement, ],
            reprompt=[statement, ],
            intent_list=[
                YesIntent(
                    response_set=['Yes, right!', ],
                    process_fn=self.mark_as_listened,
                ),
                NoIntent(
                    response_set=['OK!', ],
                    process_fn=self.mark_as_listened,
                )
            ]
        )

        super(TalkBitEngine, self).__init__(question=init_question, alexa_user=alexa_user, **kwargs)

    def mark_as_listened(self, **kwargs):
        user_listened = UserListened(action=self.user_action)
        user_listened.save()

    @staticmethod
    def fetch_user_post(user: User):
        user_post_ct = ContentType.objects.get_for_model(UserPost)
        circle = user.circle_set.all()[0]

        all_actions = UserAction.objects.mystream(user, circle)

        # Returning the latest not listened `UserPost` that happened in the last `affinity_in_days` number of days
        affinity_in_days = 5
        actions = all_actions.filter(Q(userlistened__id=None)
                                  & Q(action_object_content_type=user_post_ct)
                                  & Q(timestamp__gte=(datetime.now(tz=pytz.utc) - timedelta(days=affinity_in_days))))\
            .order_by('-timestamp')
        if actions.count() < 1:
            return None
        return actions[0]


class OutroEngine(Engine):
    def __init__(self, alexa_user: AUser, **kwargs):
        self.closings = [
            'That\'s it for now. Don\'t forget to come back by saying "Alexa, open Caressa"',

            'That\'s all for now. Not that I will miss you here.',

            'I\'m sorry to say that but I got to go now. Remember that I will be back with more soon. '
            'Call me with saying "Alexa, open Caressa"',

            'I gotta go now, but I will have more updates for you. '
            'Remember to call me saying "Alexa, open Caressa". Bye for now!',

            '{}, I am sorry but that\'s it for now. I will be back with more content the next time '
            'you say "Alexa, open Caressa".'.format(alexa_user.user.first_name),
        ]
        super(OutroEngine, self).__init__(
            question=Question(intent_list=[]), alexa_user=alexa_user, ttl=1, **kwargs
        )

    def get_random_closing(self):
        return sample(self.closings, 1)[0]


engine_registration = [
    'EmotionalEngine',
    'MedicalEngine',
    'WeightEngine',
    'JokeEngine',
    'NewsEngine',
    'AdEngine',
]
