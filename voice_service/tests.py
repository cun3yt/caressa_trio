from django.test import TestCase
from voice_service.google.intents import Intent, yes_intent, no_intent


class IntentsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sample_intent = Intent(name='sample_intent',
                                   samples=['one', 'two', 'three', 'forty five'])

    def test_intent_attrs(self):
        self.assertEqual(self.sample_intent.name, 'sample_intent')
        self.assertListEqual(self.sample_intent.samples, ['one', 'two', 'three', 'forty five'])

    def test_match(self):
        self.assertTrue(self.sample_intent.is_match('one'))
        self.assertTrue(self.sample_intent.is_match('three'))
        self.assertTrue(self.sample_intent.is_match('forty five'))

        self.assertFalse(self.sample_intent.is_match(''))
        self.assertFalse(self.sample_intent.is_match('o'))
        self.assertFalse(self.sample_intent.is_match('forty fives'))
        self.assertFalse(self.sample_intent.is_match('forty six'))

    def test_yes_intent(self):
        self.assertEqual(yes_intent.name, 'yes')
        self.assertTrue(yes_intent.is_match('hell yes'))
        self.assertTrue(yes_intent.is_match('hell yeah'))
        self.assertFalse(yes_intent.is_match('hell yooo'))

    def test_no_intent(self):
        self.assertEqual(no_intent.name, 'no')
        self.assertTrue(no_intent.is_match('nope'))
        self.assertTrue(no_intent.is_match('definitely not'))
        self.assertFalse(no_intent.is_match('definitely doughnut'))
