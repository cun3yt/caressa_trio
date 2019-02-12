from django.test import TestCase
from model_mommy import mommy
from alexa.models import User, Circle
from caressa.settings import HOSTED_ENV
from django.db.models import signals
import daiquiri
import logging

daiquiri.setup(level=logging.WARNING)


class UserModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_one = mommy.make_recipe('alexa.user', email='user1@example.com')

        cls.user_two = mommy.make_recipe('alexa.user', user_type='FAMILY',
                                         email='user2@example.com')

        cls.user_three = mommy.make_recipe('alexa.user', user_type='CAREGIVER',
                                           email='user3@example.com')

        cls.user_four = mommy.make_recipe('alexa.user', user_type='CAREGIVER_ORG',
                                          email='user4@example.com')

    def test_get_profile_object(self):
        self.assertEqual(self.user_one.get_profile_pic(), '/statics/TestProfilePic1.png')

    def test_is_senior(self):
        self.assertTrue(self.user_one.is_senior())
        self.assertFalse(self.user_one.is_family())
        self.assertFalse(self.user_one.is_provider())

    def test_is_family(self):
        self.assertTrue(self.user_two.is_family())
        self.assertFalse(self.user_two.is_senior())
        self.assertFalse(self.user_two.is_provider())

    def test_is_provider(self):
        self.assertTrue(self.user_three.is_provider())
        self.assertFalse(self.user_three.is_family())
        self.assertTrue(self.user_four.is_provider())
        self.assertFalse(self.user_four.is_senior())

    def test_create_initial_circle(self):
        signals.post_save.disconnect(sender=User, dispatch_uid='create_circle_for_user')
        user_five = User(first_name='TestFirstName1',
                         last_name='TestLastName1',
                         email='my.test.user@example.com',
                         phone_number='+14151234567',
                         profile_pic='TestProfilePic1')
        user_five.save()
        self.assertFalse(self.user_one.create_initial_circle())
        self.assertTrue(user_five.create_initial_circle())


class CircleModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_one = mommy.make_recipe('alexa.user', email='user@example.com')
        cls.circle = mommy.make(Circle)

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


class SongModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.song = mommy.make_recipe('alexa.song')
        cls.url = HOSTED_ENV + cls.song.file_name

    def test_url(self):
        self.assertEqual(self.song.url, self.url)
