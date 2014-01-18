# coding: utf-8
import json
import itertools

from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.utils.encoding import force_text


def pretty_data(request):
    if request.META.get('CONTENT_TYPE', None) == 'application/json':
        # json encoded request
        try:
            form = json.loads(force_text(request.body))
        except Exception:  # this should never fail
            form = {}
    elif request.META.get('CONTENT_TYPE', '').startswith('multipart'):
        # regular form
        form = dict(itertools.chain(request.POST.items(), request.FILES.items()))
    else:
        # other cases
        form = {}

    return u'\n'.join('%s: %s' % (key, value)
                      for key, value in form.items())


def pretty_headers_request(request):
    return u'\n'.join('%s: %s' % (key, value)
                      for key, value in request.META.items())


def pretty_headers_response(response):
    return u'\n'.join('%s: %s' % (key, value)
                      for key, value in response._headers.values())


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    try:
        validate_ipv46_address(ip)
    except ValidationError:
        ip = None
    return ip
