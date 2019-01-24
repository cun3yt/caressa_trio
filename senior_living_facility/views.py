from django.template.response import TemplateResponse
from senior_living_facility.forms import LoginForm
from django.views.decorators.csrf import csrf_exempt
from caressa.settings import WEB_CLIENT, API_URL
from alexa.models import FamilyOutreach
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError


@csrf_exempt
def facility_home(request):
    context = {
        'api_base': API_URL,
        'client_id': WEB_CLIENT['id'],
        'client_secret': WEB_CLIENT['secret'],
    }
    return TemplateResponse(request, 'home.html', context)


def family_prospect_invitation(request):
    try:
        family_outreach = FamilyOutreach.objects.get(tracking_code=request.GET.get('invitation_code'),
                                                     converted_user=None)
    except (FamilyOutreach.DoesNotExist, ValidationError, ):
        return TemplateResponse(request, 'invitation-not-valid.html')
    else:
        prospect = family_outreach.prospect
        context = {
            'prospect': prospect,
        }
        return TemplateResponse(request, 'invitation.html', context=context)
