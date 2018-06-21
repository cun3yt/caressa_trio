from random import sample
from alexa.models import AUser, Joke, News
from alexa.intents import GoodIntent, BadIntent, YesIntent, NoIntent, BloodPressureIntent, WeightIntent
from utilities.dictionaries import deep_get


class Question:
    def __init__(self, versions, intent_list, reprompt=None):
        self.versions = versions
        self.reprompt = reprompt  # todo Reprompt can be built based on what is available in intent_list!!
        self.intents = {intent.intent_identifier(): intent for intent in intent_list}
        self.asked_question = self._get_random_version()

    def _get_random_version(self):
        return sample(self.versions, 1)[0]


class Engine:
    def __init__(self, question: Question, alexa_user: AUser):
        self.question = question
        self.alexa_user = alexa_user

    def render(self, render_type='json'):
        pass


class EmotionalEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=["How are you?",
                      "How are you today?",
                      ],
            reprompt=["How do you feel?",
                      ],
            intent_list=[
                GoodIntent(question=Question(versions=['so is it good?'],
                                             intent_list=[
                                                 GoodIntent(
                                                     process_fn=self.update_on_good_intent
                                                 )
                                             ])),
                BadIntent(
                    process_fn=self.update_on_bad_intent
                )
            ],
        )

        super(EmotionalEngine, self).__init__(question=init_question, alexa_user=alexa_user)

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
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=['Would you like to hear a joke?', ],
            reprompt=["Do you want a joke?", ],
            intent_list=[
                YesIntent(
                    response_set=self.fetch_random_joke,
                    question=Question(versions=['Was it funny?',
                                                'Did you like this joke?', ],
                                      intent_list=[
                                          YesIntent(
                                              response_set=['Thanks!'],
                                              process_fn=self.save_joke_like),
                                          NoIntent(response_set=['OK']),
                                      ]),
                    # profile_builder=ProfileBuilderForJoke(alexa_user=alexa_user),
                ),
                NoIntent(response_set=['No problem', ])
            ]
        )

        super(JokeEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    @staticmethod
    def fetch_random_joke():
        joke = Joke.fetch_random()
        return '{main}<break time="1s"/>{punchline}'.format(main=joke.main, punchline=joke.punchline)

    def save_joke_like(self, **kwargs):
        from alexa.models import UserActOnContent
        act = UserActOnContent(user=self.alexa_user.user,
                               verb='laughed at',
                               object=Joke.objects.get(id=2))  # hardcoded for now..
        act.save()


class NewsEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=['Would you like to hear popular news around you?', ],  # todo should end headline
            reprompt=['Do you want to listen recent news?', ],
            intent_list=[
                YesIntent(
                    response_set=self.fetch_random_news,
                    question=Question(versions=['Did you like this news?', ],
                                      intent_list=[
                                          YesIntent(
                                              response_set=['Thanks!'],
                                              process_fn=self.save_news_like),
                                          NoIntent(response_set=['OK']),
                                      ]),
                ),
                NoIntent(response_set=['Maybe later!', ])
            ]
        )

        super(NewsEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    @staticmethod
    def fetch_random_news():
        news = News.fetch_random()
        return '{headline}<break time="1s"/>{content}'.format(headline=news.headline, content=news.content)

    def save_news_like(self, **kwargs):
        from alexa.models import UserActOnContent
        act = UserActOnContent(user=self.alexa_user.user,
                               verb='found interesting',
                               object=News.objects.get(id=6))
        act.save()


class MedicalEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=[
                "Have you taken your blood pressure measurements yet?",
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

        super(MedicalEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    def save_blood_pressure(self, **kwargs):
        self.alexa_user.set_medical_state('blood_pressure', {
            'diastolic': deep_get(kwargs, 'intent.slots.diastolic_slot.value'),
            'systolic': deep_get(kwargs, 'intent.slots.systolic_slot.value'),
            'all_params': kwargs,
        })


class WeightEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=[
                "Have you taken your weight measurement yet?",
                "Did you take your weight measurement today?",
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

        super(WeightEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    def save_weight(self, **kwargs):
        self.alexa_user.set_medical_state('weight', {
            'amount': deep_get(kwargs, 'intent.slots.weight_slot.value'),
            'unit': 'pound',
            'all_params': kwargs,
        })


class AdEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=[
                "So, many seniors suffer from night-time leg cramps. Have you had one recently?",
            ],
            reprompt=["Sorry, I didn't hear you. Did you have any night-time leg cramps lately?"],
            intent_list=[
                YesIntent(question=Question(
                    versions=[
                        "A chiropractor can ease the pain with warm massage. "
                        "Dr. Smith in San Jose has over 20 years experiences. "
                        "Would you like him to give you a call?", ],
                    intent_list=[
                        YesIntent(
                            response_set=["Great, I will ask him to give you a call.", ]
                        ),
                        NoIntent(response_set=['No problem.', ])
                    ]
                )),
                NoIntent(response_set=["It is great to hear that you don't have leg cramps. "
                                       "Just a friendly reminder: Magnesium is the mineral curing cramps."])

            ]
        )
        super(AdEngine, self).__init__(question=init_question, alexa_user=alexa_user)


engine_registration = {
    'critical': [
        'EmotionalEngine',
    ],
    'schedule-based': [
        'MedicalEngine',
        'WeightEngine',
    ],
    'filler': [
        'JokeEngine',
    ],
    'sponsored': [
        'AdEngine',
    ]
}
