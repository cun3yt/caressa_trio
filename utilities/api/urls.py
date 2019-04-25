from django.urls import reverse as django_reverse
from caressa.settings import API_URL


def reverse(name, api_base_url=None, **kwargs):
    base_url = api_base_url if api_base_url else API_URL
    return '{base_url}{relative_url}'.format(base_url=base_url, relative_url=django_reverse(name, **kwargs))
