from random import sample
from alexa.models import AUser, Joke
from alexa.intents import GoodIntent, BadIntent, YesIntent, NoIntent, BloodPressureIntent
from utilities.dictionaries import deep_get


class Question:
    def __init__(self, versions, intent_list, reprompt=None):
        self.versions = versions
        self.reprompt = reprompt    # todo Reprompt can be built based on what is available in intent_list!!
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


class JokeEngine(Engine):
    def __init__(self, alexa_user: AUser):
        init_question = Question(
            versions=['Would you like to hear a joke?', ],
            reprompt=["Do you want a joke?", ],
            intent_list=[
                YesIntent(response_set=self.fetch_random_joke),
                # todo how to connect with profile building question, e.g. "Do you like jokes?"
                NoIntent(response_set=['No problem', ])
            ]
        )

        super(JokeEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    @staticmethod
    def fetch_random_joke():
        joke = Joke.fetch_random()
        return '{main}<break time="1s">{punchline}'.format(main=joke.main, punchline=joke.punchline)


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
                                            reprompt=['Please tell me with systolic over diastolic such as 120 over 80'],
                                            intent_list=[
                                                BloodPressureIntent(
                                                    process_fn=self.save_blood_pressure
                                                )
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
                                               NoIntent(response_set=['Ok, let’s check your blood pressure later today.']),
                                           ]))
            ],
        )

        super(MedicalEngine, self).__init__(question=init_question, alexa_user=alexa_user)

    def save_blood_pressure(self, **kwargs):
        self.alexa_user.set_medical_state('blood_pressure', {
            'diastolic': deep_get(kwargs, 'intent.slots.diastolic_slot.value'),
            'systolic': deep_get(kwargs, 'intent.slots.systolic_slot.value'),
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
    ],
    'filler': [
        'JokeEngine',
    ],
    'sponsored': [
        'AdEngine',
    ]
}
