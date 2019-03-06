from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from alexa.admin import UserCreationForm
from alexa.models import User, CircleInvitation


@login_required
def main_view(request):
    return render(request, 'main.html',
                  {
                      'user': request.user,
                      'context': {
                          'userId': request.user.id,
                          'key': 'value'
                      }
                  })


def circle_member_invitation(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = User.FAMILY
            user.save()
            invitation_code = form.data.get('invitation_code')
            circle_invitation = CircleInvitation.objects.get(invitation_code=invitation_code,
                                                             converted_user_id=None, )
            circle_invitation.converted_user = user
            circle_invitation.save()
            circle_invitation.circle.add_member(member=user, is_admin=False)
            redirect_url = "{url}?success=1".format(url=reverse('app-downloads'))
            return redirect(redirect_url)

    form = UserCreationForm()
    try:
        circle_invitation = CircleInvitation.objects.get(invitation_code=request.GET.get('invitation_code'),
                                                         converted_user=None)
    except (CircleInvitation.DoesNotExist, ValidationError, ):
        return redirect('sign-up')
    else:
        invitee_email = circle_invitation.email
        context = {
            'invitee_email': invitee_email,
            'form': form,
            'invitation_code': circle_invitation.invitation_code
        }
        return TemplateResponse(request, 'circle-invitation.html', context=context)
