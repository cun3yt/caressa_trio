from django.test import TestCase
from django.db import models
from model_mommy import mommy
from alexa.models import User, Circle, CaressaUserManager, FamilyProspect
from caressa.settings import HOSTED_ENV
from django.db.models import signals
import daiquiri
import logging
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

daiquiri.setup(level=logging.WARNING)


class UserModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_one = mommy.make_recipe('alexa.user', email='user1@example.com')

        cls.user_two = mommy.make_recipe('alexa.user', user_type='FAMILY',
                                         email='user2@example.com')

        cls.user_one.senior_circle.add_member(cls.user_two, False)

        cls.user_three = mommy.make_recipe('alexa.user', user_type='CAREGIVER',
                                           email='user3@example.com')

        cls.user_four = mommy.make_recipe('alexa.user', user_type='CAREGIVER_ORG',
                                          email='user4@example.com')

    def test_get_profile_object(self):
        self.assertEqual(self.user_one.get_profile_pic(),
                         'https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_w_250.jpg')

    def test_get_profile_pictures(self):
        assert_value = {
            'w_250': 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_w_250.jpg',
            'w_25': 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_w_25.jpg',
            'raw': 'https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_raw.png',
        }
        self.assertEqual(self.user_one.get_profile_pictures(), assert_value)

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
                         profile_pic='')
        user_five.save()
        self.assertFalse(self.user_one.create_initial_circle())
        self.assertTrue(user_five.create_initial_circle())

    def test_short_name(self):
        self.assertEqual(self.user_one.get_short_name(), 'TestFirstName1')
        self.assertEqual(self.user_two.get_short_name(), self.user_two.first_name)

    def test_clean_up(self):
        user = User(email='SomEthinG@InterEstiNg.Com')
        user.clean()
        # test clean function returns the domain to a normalized (lowercase form)
        self.assertEqual(user.email, 'SomEthinG@interesting.com')

    def test_senior_circle(self):
        self.assertIsInstance(self.user_one.senior_circle, Circle)

        self.assertIsInstance(self.user_two.senior_circle, Circle)

        with self.assertRaises(KeyError):
            _ = self.user_three.senior_circle

        with self.assertRaises(KeyError):
            _ = self.user_four.senior_circle

    def test_full_name(self):
        self.assertEqual(self.user_one.full_name, 'TestFirstName1 TestLastName1')

    def test_family_circle_channel_id(self):
        self.assertEqual(User.get_family_circle_channel(123), 'channel.family.circle.123')

    def test_facility_channel_id(self):
        self.assertEqual(User.get_facility_channel(123), 'channel.slf.123')

    def test_senior_communication_channel(self):
        circle_family_str = 'channel.family.circle.{circle_id}'
        comm_channel = self.user_one.senior_communication_channel
        self.assertEqual(comm_channel, circle_family_str.format(circle_id=self.user_one.senior_circle.id))

        with self.assertRaises(AssertionError):
            _ = self.user_two.senior_communication_channel

        with self.assertRaises(AssertionError):
            _ = self.user_three.senior_communication_channel

        with self.assertRaises(AssertionError):
            _ = self.user_four.senior_communication_channel

    def test_communication_channels(self):
        circle_family_str = 'channel.family.circle.{circle_id}'
        circle_slf_str = 'channel.slf.{facility_id}'

        comm_ch1 = self.user_one.communication_channels()     # senior's communication channels
        facility1 = self.user_one.senior_living_facility
        self.assertListEqual(comm_ch1, [circle_family_str.format(circle_id=self.user_one.senior_circle.id),
                                        circle_slf_str.format(facility_id=facility1.facility_id), ])

        comm_ch2 = self.user_two.communication_channels()   # family's communication channels
        circle = self.user_two.circle_set.all()[0]
        self.assertListEqual(comm_ch2, [circle_family_str.format(circle_id=circle.id), ])

        comm_ch3 = self.user_three.communication_channels()   # caregiver's communication channels
        facility3 = self.user_three.senior_living_facility
        self.assertListEqual(comm_ch3, [circle_slf_str.format(facility_id=facility3.facility_id), ])

        comm_ch4 = self.user_four.communication_channels()   # caregiver org's communication channels
        facility4 = self.user_four.senior_living_facility
        self.assertListEqual(comm_ch4, [circle_slf_str.format(facility_id=facility4.facility_id), ])

    def test_repr(self):
        self.assertEqual(repr(self.user_one), 'Testfirstname1')

    def test_str(self):
        self.assertEqual(str(self.user_one), 'TestFirstName1 TestLastName1')


class CaressaUserManagerTest(TestCase):
    def test_manager_user_creation_none_email(self):
        class U(models.Model):
            email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
            password = models.CharField(_('password'), max_length=128)
            is_superuser = models.BooleanField(default=False, )
            is_active = models.BooleanField(default=True, )
            objects = CaressaUserManager()

            def set_password(self, passwd):
                pass

            def save(self, *args, **kwargs):
                pass

        self.assertRaises(ValueError, U.objects.create_user, email=None, password='something')
        user1 = U.objects.create_user(email='something1234@example.com', password='password1!')
        self.assertFalse(user1.is_superuser, 'create_user is supposed to create non-superuser')

        self.assertRaises(ValueError, U.objects.create_superuser, email=None, password='something')
        user2 = U.objects.create_superuser(email='wawawa@example.com', password='passss')
        self.assertTrue(user2.is_superuser, 'create_superuser is supposed to create superuser')


class CircleModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_one = mommy.make_recipe('alexa.user', email='user@example.com')    # this is a senior user
        cls.user_two = mommy.make_recipe('alexa.user2', email='user2@example.com')
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

    def test_repr(self):
        _circle = self.user_one.senior_circle    # senior user comes with a circle
        poi_user_str = str(self.user_one)
        self.assertEqual(repr(_circle), 'Circle of [{}] with 1 member(s)'.format(poi_user_str))
        _circle.add_member(member=self.user_two, is_admin=True)
        self.assertEqual(repr(_circle), 'Circle of [{}] with 2 member(s)'.format(poi_user_str))

    def test_admins(self):
        senior = mommy.make_recipe('alexa.user', email='super_senior@example.com')
        _circle = senior.senior_circle
        self.assertEqual(_circle.admins.count(), 0)

        admin_user1 = mommy.make_recipe('alexa.user2', email='admin1@admin.com')
        _circle.add_member(member=admin_user1, is_admin=True)
        self.assertEqual(_circle.admins.count(), 1)

        admin_user2 = mommy.make_recipe('alexa.user2', email='admin2@admin.com')
        _circle.add_member(member=admin_user2, is_admin=True)
        self.assertEqual(_circle.admins.count(), 2)

        admin_user3 = mommy.make_recipe('alexa.user2', email='user@regular.com')
        _circle.add_member(member=admin_user3, is_admin=False)
        self.assertEqual(_circle.admins.count(), 2)


class SongModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.song = mommy.make_recipe('alexa.song')
        cls.url = HOSTED_ENV + cls.song.file_name

    def test_url(self):
        self.assertEqual(self.song.url, self.url)


class FamilyProspectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.senior = mommy.make_recipe('alexa.user', email='senior_dunkin@donuts.com')

    def test_clean(self):
        prospect_dunkin = mommy.make(FamilyProspect, name='Dunkin Donuts', email='', senior=self.senior)

        self.assertRaises(ValidationError, prospect_dunkin.clean)

        prospect_sister = mommy.make(FamilyProspect, name='Sister Donuts',
                                     email='prospect_dunkin@donuts.com', senior=self.senior)
        try:
            prospect_sister.clean()
        except ValidationError:
            self.fail("FamilyProspect is valid with just email even when no phone number is specified")

    def test_reach_prospect_with_admin(self):
        self.senior.senior_circle.add_member(member=self.senior, is_admin=False)
        family_user = mommy.make_recipe('alexa.family_user')
        self.senior.senior_circle.add_member(family_user, is_admin=True)
        prospect_sister = mommy.make(FamilyProspect, name='Sister Donuts',
                                     email='prospect_dunkin@donuts.com', senior=self.senior)
        ret_val = prospect_sister.reach_prospect()
        self.assertFalse(ret_val, "We don't reach the prospect if there is already an admin in the circle")


class FetchRandomMixinTestCase(TestCase):   # todo: alexa.mixins
    pass
