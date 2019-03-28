from django.test import TestCase
from senior_living_facility.models import SeniorLivingFacility, ServiceRequest
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
