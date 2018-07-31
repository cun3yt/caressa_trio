from django.test import TestCase
from alexa.engines import Question, FactEngine
from alexa.intents import Intent, YesIntent
from model_mommy import mommy
from alexa.slots import SlotType, Slot
from alexa.models import User, AUser, Circle, EngineSession, Fact, AUserEmotionalState, AUserMedicalState, Song, \
    CircleMembership
from caressa.settings import HOSTED_ENV
from unittest.mock import patch
from django.db.models import signals



class BaseIntentTestCase(TestCase):
    def setUp(self):
        self.simplest_intent = Intent(name='SimpleIntent',
                                      response_set=['something', 'else', ],
                                      slots=None,
                                      follow_engine=None,
                                      samples=None,
                                      process_fn=None,
                                      question=None,
                                      end_session=False)
        self.complex_intent = Intent(name='Complex-Intent',
                                     response_set=lambda: 'response set',
                                     slots=Slot(name='slot-name',
                                                slot_type=SlotType(name='slot-type-name',
                                                                   values=['abc', 'def'])),
                                     follow_engine='SomeEngine',
                                     samples=['Hello', 'Hi'],
                                     process_fn=lambda: 'processed',
                                     question=Question(intent_list=[]),
                                     end_session=True,
                                     profile_builder=lambda: 'profile is built')

    def test_intent_identifier(self):
        self.assertEqual(Intent.intent_identifier(), 'intent-identifier')

    def test_true_end_state(self):
        self.assertTrue(self.simplest_intent.is_end_state(), True)

    # @patch(sample, return_value='something')
    # def test_list_response_set(self):
    #     self.assertEqual(self.simplest_intent.get_random_response(), 'something')

    def test_none_engine_session(self):
        self.assertIsNone(self.simplest_intent.engine_session)

    def test_none_profile_builder(self):
        self.assertIsNone(self.simplest_intent.profile_builder)

    # ---
    def test_false_end_state(self):
        self.assertFalse(self.complex_intent.is_end_state(), False)

    def test_fn_response_set(self):
        self.assertEqual(self.complex_intent.get_random_response(), 'response set')

    def test_engine_session(self):
        pass    # todo not written since this property is not in use yet.

    def test_profile_builder(self):
        self.assertIsNotNone(self.complex_intent.profile_builder)
        self.assertEqual(self.complex_intent.profile_builder(), 'profile is built')


class QuestionTestCase(TestCase):
    def setUp(self):
        def version_fn():
            return 'hello'

        def reprompt_fn():
            return 'hello reprompt'

        self.q_no_version = Question(versions=None, intent_list=[], reprompt=['hello'])
        self.q_fn_version = Question(versions=version_fn, intent_list=[])
        self.q_fn_reprompt = Question(versions=None, intent_list=[], reprompt=reprompt_fn)
        self.q = Question(versions=['a', 'b', 'c'],
                          intent_list=[
                              YesIntent(response_set=['x', 'y'],
                                        end_session=True)
                          ])

    def test_no_version_fields(self):
        self.assertEqual(self.q_no_version.versions, None)
        self.assertEqual(self.q_no_version.reprompt, ['hello'])
        self.assertEqual(self.q_no_version.intents, {})
        self.assertEqual(self.q_no_version.asked_question, '')

    def test_fn_version_field(self):
        self.assertEqual(self.q_fn_version.asked_question, 'hello')

    def test_fn_reprompt_field(self):
        self.assertEqual(self.q_fn_reprompt.reprompt, 'hello reprompt')

    def test_question_fields(self):
        self.assertEqual(self.q.versions, ['a', 'b', 'c'])
        self.assertEqual(len(self.q.intents), 1)
        self.assertIsInstance(self.q.intents['yes_intent'], YesIntent)
        self.assertIn(self.q.asked_question, ['a', 'b', 'c'])


class FactEngineTestCase(TestCase):
    def setUp(self):
        self.a_user = mommy.make(AUser, _fill_optional=['alexa_id', ])  # type: AUser
        self.fact = mommy.make(Fact,
                               entry_text='entry-text-here',
                               fact_list=['content-1',
                                          'content-2',
                                          'content-3',
                                          'content-4',
                                          'content-5',
                                          'content-6', ],
                               ending_yes_no_question='question-here')  # type: Fact
        self.content = self.fact.get_random_content()
        self.engine_session = mommy.make(EngineSession,
                                         user=self.a_user,
                                         name='FactEngine',
                                         state='continue')

    def test_question_setup(self):
        with patch.object(Fact, 'fetch_random', return_value=self.fact), \
             patch.object(Fact, 'get_random_content', return_value=self.content):

            engine = FactEngine(alexa_user=self.a_user, engine_session=self.engine_session)
            intent_keys = [x for x in engine.question.intents.keys()]

            self.assertEqual(engine.question.asked_question, "{introduction}. {content}. {question}".format(
                introduction=self.fact.entry_text,
                content=self.content,
                question=self.fact.ending_yes_no_question
            ))
            self.assertEqual(engine.question.reprompt, self.fact.ending_yes_no_question)
            self.assertEqual(engine.ttl, 60)
            self.assertEqual(engine.alexa_user, self.a_user)
            self.assertTrue(isinstance(engine.question, Question))
            self.assertIsNotNone(engine.engine_session)
            self.assertEqual(len(engine.question.intents), 4)
            self.assertIn('no_intent', intent_keys)
            self.assertIn('yes_intent', intent_keys)


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user_one = mommy.make_recipe('alexa.user')

        self.user_two = mommy.make_recipe('alexa.user', user_type='FAMILY')

        self.user_three = mommy.make_recipe('alexa.user', user_type='CAREGIVER')

        self.user_four = mommy.make_recipe('alexa.user', user_type='CAREGIVER_ORG')

    def test_get_profile_object(self):
        self.assertEqual(self.user_one.get_profile_pic(), '/statics/TestProfilePic1.png')

    def test_is_senior(self):
        self.assertTrue(self.user_one.is_senior(), True)
        self.assertFalse(self.user_one.is_family(), False)
        self.assertFalse(self.user_one.is_provider(), False)

    def test_is_family(self):
        self.assertTrue(self.user_two.is_family(), True)
        self.assertFalse(self.user_two.is_senior(), False)
        self.assertFalse(self.user_two.is_provider(), False)

    def test_is_provider(self):
        self.assertTrue(self.user_three.is_provider(), True)
        self.assertFalse(self.user_three.is_family(), False)
        self.assertTrue(self.user_four.is_provider(), True)
        self.assertFalse(self.user_four.is_senior(), False)

    def test_create_initial_circle(self):
        signals.post_save.disconnect(sender=User, dispatch_uid='create_circle_for_user')
        user_five = User(first_name='TestFirstName1',
                         last_name='TestLastName1',
                         email='TestEMail1',
                         phone_number='+14151234567',
                         profile_pic='TestProfilePic1')
        user_five.save()
        self.assertFalse(self.user_one.create_initial_circle(), False)
        self.assertTrue(user_five.create_initial_circle(), True)


class CircleModelTestCase(TestCase):
    def setUp(self):
        self.user_one = mommy.make_recipe('alexa.user')
        self.circle = mommy.make(Circle)

    def test_add_member(self):
        self.assertEqual(self.circle.members.count(), 0, "Initial State: No member in a circle")
        self.circle.add_member(member=self.user_one, is_admin=True)
        self.assertEqual(self.circle.members.count(), 1, "Number of circle members must be only one")
        self.assertIsInstance(self.circle.members.all()[0], User)
        self.assertEqual(self.circle.members.all()[0].id, self.user_one.id,
                         "The user added to the circle is the same as the initial one")
        self.assertFalse(self.circle.add_member(member=self.user_one, is_admin=True),
                         'Same member add validation failed.')

    def test_is_member(self):
        self.assertEqual(self.circle.members.count(), 0, "Initial State: No member in a circle")
        self.circle.add_member(member=self.user_one, is_admin=True)
        self.assertEqual(self.circle.members.count(), 1, "After Add Member State: No member in circle.")
        self.assertTrue(self.circle.is_member(self.user_one), "Not the member added in test")


class AUserModelTestCase(TestCase):
    def setUp(self):
        self.auser_one = mommy.make_recipe('alexa.auser')
        self.auser_two = mommy.make(AUser, engine_schedule='')
        self.auser_emotional_state = mommy.make(AUserEmotionalState)
        self.auser_medical_state = mommy.make(AUserMedicalState)
        self.engine_session_one = mommy.make_recipe('alexa.engine_session')

    def test_last_engine_session(self):
        user = self.engine_session_one.user
        last_engine_session = user.last_engine_session()
        self.assertEqual(last_engine_session.id, self.engine_session_one.id)

    def test_set_emotion(self):
        set_emotion = self.auser_one.set_emotion('anxiety', 50.05)
        self.assertEqual(set_emotion.attribute, 'anxiety')

    def test_update_emotion(self):
        value = 50.05
        emotion = 'anxiety'
        percentage = -5.0
        self.auser_one.set_emotion(emotion=emotion, value=value)
        update_emotion = self.auser_one.update_emotion(emotion=emotion, percentage=percentage)
        updated_value = value * (1+percentage/100)
        self.assertEqual(updated_value, update_emotion.value)

    def test_set_medical_state(self):
        measurement = 'weight'
        data = {
            "unit": "pound",
            "amount": "185",
            "all_params": {"intent": {"name": "weight_intent",
                                      "slots": {"weight_slot": {"name": "weight_slot",
                                                                "value": "185",
                                                                "confirmationStatus": "NONE"}
                                                },
                                      "confirmationStatus": "NONE"
                                      }
                           }
        }
        set_medical_state = self.auser_one.set_medical_state(measurement=measurement, data=data)
        self.assertEqual(set_medical_state.measurement, measurement)
        self.assertEqual(set_medical_state.data, data)

    def test_profile_get_set(self):
        self.auser_one.profile_set('joke.simple', True)
        self.assertTrue(self.auser_one.profile_get('joke.simple'))
        self.assertTrue(isinstance(self.auser_one.profile_get('joke'), dict))
        self.assertIsNone(self.auser_one.profile_get('joke.smt'))
        self.assertIsNone(self.auser_one.profile_get('none.value'))

    def test_create_initial_engine_scheduler(self):
        self.assertFalse(self.auser_one.create_initial_engine_scheduler(), False)
        self.assertTrue(self.auser_two.create_initial_engine_scheduler(), True)


class SongModelTestCase(TestCase):
    def setUp(self):
        self.song = mommy.make_recipe('alexa.song')
        self.url = HOSTED_ENV + self.song.file_name

    def test_url(self):
        self.assertEqual(self.song.url, self.url)
