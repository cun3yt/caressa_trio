from django.test import TestCase
from alexa.engines import Question
from alexa.intents import Intent
from alexa.slots import SlotType, Slot
from unittest.mock import patch
from random import sample


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
