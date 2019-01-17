from django.template.response import TemplateResponse
from senior_living_facility.forms import LoginForm
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def facility_home(request):
    return TemplateResponse(request,
                            'home.html')
