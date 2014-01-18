# coding: utf-8
import logging
from django.conf import settings

from django.core.urlresolvers import resolve, Resolver404
from httplog.models import Entry


class RequestResponseLoggingMiddleware(object):
    apps = getattr(settings, 'HTTPLOG_APPS', [])
    names = getattr(settings, 'HTTPLOG_URLNAMES', [])

    def is_request_loggable(self, request):
        """
        Match request by either app name, or urlname
        """

        # Forward-compatible request.resolver_match
        request.resolver_match = getattr(request, 'resolver_match', None) or resolve(request.path)
        return (request.resolver_match.app_name in self.apps
                or request.resolver_match.url_name in self.names)

    def process_request(self, request):
        """ A bit of magic

            Accessing request.body here we can later access it in process_response
        """
        if self.is_request_loggable(request):
            _ = request.body  # noqa
        return None

    def process_response(self, request, response):
        try:
            if not self.is_request_loggable(request):
                return response
            Entry.objects.create_from_request_response(
                request,
                response
            )
        except Resolver404:
            # no need to log broken requests
            pass
        except Exception as e:
            logging.exception(e)  # TODO: proper logging
            pass
        return response
