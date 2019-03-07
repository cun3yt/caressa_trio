from django.template.response import TemplateResponse
from django.shortcuts import redirect
from alexa.admin import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from caressa.settings import WEB_CLIENT, API_URL
from alexa.models import FamilyOutreach
from django.core.exceptions import ValidationError
from django.urls import reverse
from alexa.models import User


@csrf_exempt
def facility_home(request):
    context = {
        'api_base': API_URL,
        'client_id': WEB_CLIENT['id'],
        'client_secret': WEB_CLIENT['secret'],
    }
    return TemplateResponse(request, 'seniors-list.html', context)


def sign_up(request):
    form = UserCreationForm()
    return TemplateResponse(request, 'invitation-not-valid.html', context={'form': form})


def app_downloads(request):
    context = {'message': 'Your account is created'} if request.GET.get('success') else {}

    # todo: Implement the download template
    return TemplateResponse(request, 'app-downloads.html', context=context)


def family_prospect_invitation(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = User.FAMILY
            user.save()
            form.save_m2m()
            tracking_code = form.data.get('invitation_code')
            family_outreach = FamilyOutreach.objects.get(tracking_code=tracking_code,
                                                         converted_user=None)
            family_outreach.converted_user = user
            family_outreach.save()
            senior = family_outreach.prospect.senior
            senior.senior_circle.add_member(member=user, is_admin=True)
            redirect_url = "{url}?success=1".format(url=reverse('app-downloads'))
            return redirect(redirect_url)

    form = UserCreationForm()
    try:
        family_outreach = FamilyOutreach.objects.get(tracking_code=request.GET.get('invitation_code'),
                                                     converted_user=None)
    except (FamilyOutreach.DoesNotExist, ValidationError, ):
        return redirect('sign-up')
    else:
        prospect = family_outreach.prospect
        context = {
            'prospect': prospect,
            'form': form,
            'invitation_code': family_outreach.tracking_code
        }
        return TemplateResponse(request, 'invitation.html', context=context)
