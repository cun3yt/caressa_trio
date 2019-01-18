from django.template.response import TemplateResponse
from senior_living_facility.forms import LoginForm
from django.views.decorators.csrf import csrf_exempt
from caressa.settings import WEB_CLIENT


@csrf_exempt
def facility_home(request):
    context = {
        'client_id': WEB_CLIENT['id'],
        'client_secret': WEB_CLIENT['secret'],
    }
    return TemplateResponse(request, 'home.html', context)
