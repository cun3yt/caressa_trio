from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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
