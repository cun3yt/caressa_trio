from django.template.response import TemplateResponse
from senior_living_facility.forms import LoginForm


def facility_home(request):
    if request.user.is_anonymous_user:
        return TemplateResponse(request,
                                'login.html',
                                {'facility_name': 'Brookdale Fremont',
                                 'form': LoginForm()})
    return TemplateResponse(request,
                            'home.html',
                            {'facility_name': 'Brookdale Fremont',
                             'user': request.user})
