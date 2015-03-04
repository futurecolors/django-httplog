# coding: utf-8
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include
from django.http import HttpResponse


def dummy(request):
    return HttpResponse()


urlpatterns = patterns('',
    url('^api/.+/$', dummy, name='dummy'),
    url('', include('django.contrib.auth.urls', app_name='auth', namespace='auth'))
)
