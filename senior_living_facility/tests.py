from datetime import date

from django.test import TestCase, RequestFactory
from ipdb import set_trace

from caressa.settings import API_URL, S3_PRODUCTION_BUCKET, S3_REGION
from senior_living_facility.api.serializers import PhotoGallerySerializer, PhotosDaySerializer, MessageThreadSerializer, \
    FacilitySerializer, FacilityMessageSerializer
from senior_living_facility.models import SeniorLivingFacility, ServiceRequest, Photo, PhotoGallery, MessageThread, \
    MessageThreadParticipant, Message, ContentDeliveryRule
from model_mommy import mommy
from unittest.mock import patch
import pytz
import re


class TestSeniorLivingFacility(TestCase):
    def test_phone_numbers(self):
        facility = mommy.make(SeniorLivingFacility, facility_id='CA.Fremont.XYZ')
        facility2 = mommy.make(SeniorLivingFacility, facility_id='AZ.Phoenix.ABC')
        fac_user1 = mommy.make('alexa.user', user_type='CAREGIVER', email='user1@facility.com',
                               senior_living_facility=facility, phone_number='+1 123-456-7889')
        fac_user2 = mommy.make('alexa.user', user_type='CAREGIVER_ORG', email='user2@facility.com',
                               senior_living_facility=facility, phone_number='+1 987-788-4561')
        fac_user3_no_phone = mommy.make('alexa.user', user_type='CAREGIVER', email='user3@example.com',
                                        senior_living_facility=facility)
        another_fac_user1 = mommy.make('alexa.user', user_type='CAREGIVER', email='user1@another-facility.com',
                                       senior_living_facility=facility2, phone_number='+1 452-321-7593')
        another_fac_user2 = mommy.make('alexa.user', user_type='CAREGIVER_ORG', email='user2@another-facility.com',
                                       senior_living_facility=facility2, phone_number='+1 294-130-0134')
        senior1 = mommy.make('alexa.user', user_type='SENIOR', email='senior1@example.com',
                             senior_living_facility=facility, phone_number='+1 493-903-1032')
        senior2_no_phone = mommy.make('alexa.user', user_type='SENIOR', email='senior2@example.com',
                                      senior_living_facility=facility)
        another_senior1 = mommy.make('alexa.user', user_type='SENIOR', email='senior1@example2.com',
                                     senior_living_facility=facility, phone_number='+1984-324-4382')
        family1 = mommy.make('alexa.user', user_type='FAMILY', email='family1@example.com',
                             phone_number='+1 842-123-4829')

        phone_numbers = set(re.sub(r'-', '', number.as_international) for number in facility.phone_numbers)
        self.assertSetEqual(set(['+1 1234567889', '+1 9877884561']), phone_numbers)


class TestServiceRequest(TestCase):
    @patch('senior_living_facility.models.send_sms')
    def test_process(self, mock_send_sms):
        facility = mommy.make(SeniorLivingFacility, facility_id='CA.Fremont.XYZ')
        fac_user1 = mommy.make('alexa.user', user_type='CAREGIVER', email='user1@facility.com',
                               senior_living_facility=facility, phone_number='+1 415-533-7523')
        senior1 = mommy.make('alexa.user', user_type='SENIOR', email='senior1@example.com',
                             senior_living_facility=facility, phone_number='+1 493-903-1032', room_no=123,
                             first_name='Elizabeth', last_name='Johnson')

        service_request = mommy.make(ServiceRequest, requester=senior1, receiver=facility)
        service_request.process()

        time_format = "%I:%M %p"  # e.g. '06:30 PM'
        tz = pytz.timezone(facility.timezone)
        expected_request_time = service_request.created.astimezone(tz).strftime(time_format)

        context = {
            'name': 'Elizabeth Johnson',
            'room_no': 123,
            'time': expected_request_time,
        }

        mock_send_sms.assert_called_once_with('+1 415-533-7523', context, 'sms/service-request.txt')


class TestFacilitySerializer(TestCase):
    def setUp(self) -> None:
        self.facility = mommy.make(SeniorLivingFacility,
                                   facility_id='CA.Fremont.XYZ',
                                   calendar_url='https://samplecalendarurl.com')

        mommy.make('alexa.user', user_type='SENIOR', email='senior1@example.com',
                   senior_living_facility=self.facility, phone_number='+1 493-903-1032',
                   first_name='Pamela')
        mommy.make('alexa.user', user_type='SENIOR', email='senior2@example.com',
                   senior_living_facility=self.facility, phone_number='+1 493-903-1032',
                   first_name='Maggie')
        self.photo_gallery_url = '{api_url}/api/photo-galleries/{id}/'.format(api_url=API_URL,
                                                                              id=self.facility.id, )
        self.profile_pic = "{region}/{bucket}/images/facilities/no_user/" \
                           "default_profile_pic_w_250.jpg".format(region=S3_REGION,
                                                                  bucket=S3_PRODUCTION_BUCKET,)

        self.real_time_communication_channels = {
            'check-in': {
                'channel': 'channel.slf.CA.Fremont.XYZ',
                'event': 'check-in-status',
            },
            'device-status': {
                'channel': 'channel.slf.CA.Fremont.XYZ',
                'event': 'device-status',
            }
        }

        self.serializer = FacilitySerializer(instance=self.facility)

    def test_contains_exptected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id',
                                            'name',
                                            'number_of_residents',
                                            'number_of_unread_notifications',
                                            'timezone',
                                            'photo_gallery_url',
                                            'profile_picture',
                                            'real_time_communication_channels',
                                            'mock_status',])

    def test_field_contents(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.facility.id)
        self.assertEqual(data['name'], self.facility.name)
        self.assertEqual(data['number_of_residents'], 2)
        self.assertEqual(data['number_of_unread_notifications'], 3)
        self.assertEqual(data['timezone'], self.facility.timezone)
        self.assertEqual(data['photo_gallery_url'], self.photo_gallery_url )
        self.assertEqual(data['profile_picture'], self.profile_pic)
        self.assertEqual(data['real_time_communication_channels'], self.real_time_communication_channels)
        self.assertEqual(data['mock_status'], True)

    def test_validation(self):
        serializer_data = 123
        invalid_serializer = FacilitySerializer(data=serializer_data)

        self.assertFalse(invalid_serializer.is_valid())


class TestFacilityMessageSerializer(TestCase):
    def setUp(self) -> None:
        self.facility = mommy.make(SeniorLivingFacility,
                                   facility_id='CA.Fremont.XYZ',
                                   calendar_url='https://samplecalendarurl.com')
        self.staff = mommy.make('alexa.user', user_type='CAREGIVER_ORG', email='staff1@example.com',
                                senior_living_facility=self.facility, phone_number='+1 493-903-1032',
                                first_name='Jane')
        self.senior = mommy.make('alexa.user', user_type='SENIOR', email='senior1@example.com',
                                 senior_living_facility=self.facility, phone_number='+1 493-903-1032',
                                 first_name='Pamela')

        self.rf = RequestFactory()
        self.rf.user = self.staff
        self.rf.data = {
            "to": self.senior.id,
            "message_type": "Message",
            "message": {
                "format": "text",
                "content": "Hi Pamela, I hope you are feeling okay."
            },
            "request_reply": False
        }

        self.context = {
            'request': self.rf
        }

    def test_message_format_text(self):
        serializer = FacilityMessageSerializer(context=self.context)
        created_message_instance = serializer.create({})

        self.assertEqual(created_message_instance.content, 'Hi Pamela, I hope you are feeling okay.')
        self.assertEqual(created_message_instance.source_user, self.staff)

    def test_message_format_audio(self):
        self.rf.data = {
            "to": self.senior.id,
            "message_type": "Message",
            "message": {
                "format": "audio",
                "content": "test_audio_key.mp3"
            },
            "request_reply": False
        }

        serializer = FacilityMessageSerializer(context=self.context)

        created_message_instance = serializer.create({})  # todo mock aws call
        self.assertIsNone(created_message_instance.content)
        self.assertEqual(created_message_instance.source_user, self.staff)


class TestAdminAppSeniorListSerializer(TestCase):
    def setUp(self) -> None:
        pass

    def test_contains_exptected_fields(self):
        pass

    def test_field_contents(self):
        pass

    def test_validation(self):
        pass


class TestFacilityStaffSerializer(TestCase):
    def setUp(self) -> None:
        pass

    def test_contains_exptected_fields(self):
        pass

    def test_field_contents(self):
        pass

    def test_validation(self):
        pass


class TestMessageThreadSerializer(TestCase):
    def setUp(self) -> None:
        facility = mommy.make(SeniorLivingFacility, facility_id='CA.Fremont.XYZ')
        senior = mommy.make('alexa.user', user_type='SENIOR', email='senior1@example.com',
                            senior_living_facility=facility, phone_number='+1 493-903-1032',
                            first_name='Pamela')
        fac_user = mommy.make('alexa.user', user_type='CAREGIVER_ORG', email='user2@facility.com',
                              senior_living_facility=facility, phone_number='+1 987-788-4561')

        content_delivery_rule_1 = mommy.make(ContentDeliveryRule, recipient_ids=[senior.id])
        self.message_thread_1 = mommy.make(MessageThread)
        mommy.make(MessageThreadParticipant,
                   message_thread=self.message_thread_1,
                   user=senior,
                   senior_living_facility=facility,
                   is_all_recipients=False, )
        mommy.make(Message,
                   message_thread=self.message_thread_1,
                   content='message_text_1',
                   content_audio_file=None,
                   source_user=fac_user,
                   delivery_rule=content_delivery_rule_1, )

        self.message_thread_1_url = '{API_URL}/api/message-thread/{id}/messages/'.format(API_URL=API_URL,
                                                                                         id=self.message_thread_1.id)

        content_delivery_rule_2 = mommy.make(ContentDeliveryRule, recipient_ids=None)
        self.message_thread_2 = mommy.make(MessageThread)
        mommy.make(MessageThreadParticipant,
                   message_thread=self.message_thread_2,
                   user=None,
                   senior_living_facility=facility,
                   is_all_recipients=True, )
        mommy.make(Message,
                   message_thread=self.message_thread_2,
                   content='message_text_2',
                   content_audio_file=None,
                   source_user=fac_user,
                   delivery_rule=content_delivery_rule_2, )
        # self.message_thread_2_url todo implement/activate (requires all residents message thread url serialized)

        self.serializer_1 = MessageThreadSerializer(instance=self.message_thread_1)
        self.serializer_2 = MessageThreadSerializer(instance=self.message_thread_2)

    def test_contains_exptected_fields(self):
        data_1 = self.serializer_1.data
        data_2 = self.serializer_2.data

        self.assertCountEqual(data_1.keys(), ['pk', 'resident', 'messages'])
        self.assertCountEqual(data_1['messages'].keys(), ['url'])
        self.assertCountEqual(data_2.keys(), ['pk', 'resident', 'messages'])
        self.assertCountEqual(data_2['messages'].keys(), ['url'])

    def test_field_contents(self):
        data_1 = self.serializer_1.data
        data_2 = self.serializer_2.data

        self.assertEqual(data_1['pk'], self.message_thread_1.id)
        self.assertEqual(data_1['resident']['first_name'], 'Pamela')
        self.assertEqual(data_1['messages']['url'], self.message_thread_1_url)

        self.assertEqual(data_2['pk'], self.message_thread_2.id)
        self.assertEqual(data_2['resident'], 'All Residents')
        # self.assertEqual(data_2['messages'], self.message_thread_2_url) todo implement/activate (line 111)

    def test_validation(self):
        self.serializer_data = 123
        invalid_serializer = MessageThreadSerializer(data=self.serializer_data)

        self.assertFalse(invalid_serializer.is_valid(), "Dictionary value is valid. Need to pass other than "
                                                        "Dictionary to check if validation works")


class TestPhotoGallerySerializer(TestCase):
    def setUp(self) -> None:
        self.facility = mommy.make(SeniorLivingFacility, facility_id='CA.Fremont.XYZ')
        self.photo_gallery = mommy.make(PhotoGallery, senior_living_facility=self.facility)
        self.gallery_view_date = date(2019, 4, 24)
        self.photo = mommy.make(Photo, photo_gallery=self.photo_gallery,
                                date=self.gallery_view_date,
                                url='http://dummyimage.com/143x220.jpg/dddddd/000000')

        relative_url = '/api/photo-galleries/{id}/days/{iso_date}/'.format(id=self.facility.id,
                                                                           iso_date=self.gallery_view_date.isoformat())
        self.date = '2019-04-24'
        self.day_url = '{API_URL}{relative_url}'.format(API_URL=API_URL, relative_url=relative_url)

        self.serializer_data = {
            'day': {
                'date': '2019-06-10',
                'url': 'http://localhost:9900/api/photo-galleries/3/days/2019-06-10/'
            }
        }
        self.serializer = PhotoGallerySerializer(instance=self.photo)

    def test_contains_expected_fields(self):
        data = self.serializer.data

        self.assertCountEqual(data.keys(), ['day'])

    def test_day_field_content(self):
        data = self.serializer.data

        self.assertEqual(data['day']['url'], self.day_url)
        self.assertEqual(data['day']['date'], self.date)

    def test_validation(self):
        self.serializer_data = 123
        invalid_serializer = PhotoGallerySerializer(data=self.serializer_data)

        self.assertFalse(invalid_serializer.is_valid(), "Dictionary value is valid. Need to pass other than "
                                                        "Dictionary to check if validation works")


class TestPhotosDaySerializer(TestCase):
    def setUp(self) -> None:
        self.facility = mommy.make(SeniorLivingFacility, facility_id='CA.Fremont.XYZ')
        self.photo_gallery = mommy.make(PhotoGallery, senior_living_facility=self.facility)
        self.photo_attributes = {
            'photo_gallery': self.photo_gallery,
            'date': date(2019, 4, 24),
            'url': 'http://dummyimage.com/143x220.jpg/dddddd/000000'
        }

        self.serializer_data = {
            'url': 'http://dummyimage.com/232x227.png/5fa2dd/ffffff'
        }

        self.photo = Photo.objects.create(**self.photo_attributes)
        self.serializer = PhotosDaySerializer(instance=self.photo)

    def test_contains_expected_fields(self):
        data = self.serializer.data

        self.assertCountEqual(data.keys(), ['url'])

    def test_photo_field_content(self):
        data = self.serializer.data

        self.assertEqual(data['url'], self.photo_attributes['url'])

    def test_validation(self):
        self.serializer_data = 'http://dummyimage.com/143x220.jpg/dddddd/000000'

        invalid_serializer = PhotosDaySerializer(data=self.serializer_data)

        self.assertFalse(invalid_serializer.is_valid(),)

