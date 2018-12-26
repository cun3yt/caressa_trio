from alexa.models import User
from senior_living_facility.models import SeniorLivingFacility, SeniorLivingFacilityContent, SeniorActOnFacilityContent
from datetime import datetime
import pytz


class Content:  # Content for a give user
    def __init__(self, user: User):
        self.frequency = 'daily'
        self.user = user

    def does_exist(self):
        raise Exception('Not Implemented!!')

    def is_consumed(self):
        raise Exception('Not Implemented!!')

    def get_details(self):
        raise Exception('Not Implemented!!')

    def mark_consumed(self, payload=None):
        raise Exception('Not Implemented!!')


class DailyCalendarContent(Content):
    def __init__(self, user: User):
        self.frequency = 'daily'
        super(DailyCalendarContent, self).__init__(user=user)

    def does_exist(self):
        return True     # daily calendar update always exists

    def is_consumed(self):
        facility = self.user.senior_living_facilities.all()[0]  # type: SeniorLivingFacility
        tz = pytz.timezone(facility.timezone)
        today = datetime.now(tz).date()

        content_set = SeniorActOnFacilityContent.objects.filter(senior=self.user,
                                                                act='Heard',
                                                                content__content_type='Daily-Calendar-Summary',
                                                                created__date=today)

        return True if content_set.count() >= 1 else False

    def get_details(self) -> SeniorLivingFacilityContent:
        facility = self.user.senior_living_facilities.all()[0]  # type: SeniorLivingFacility
        return facility.today_event_summary()

    def mark_consumed(self, payload=None):
        content = payload.get('content')
        act = SeniorActOnFacilityContent(act='Heard',
                                         content=content,
                                         senior=self.user)
        act.save()
        return act
