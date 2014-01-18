# coding: utf-8
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from httplog import utils


class LogManager(models.Manager):

    def create_from_request_response(self, request, response):

        # Do not store binary data in database
        is_binary_upload = (request.META.get('CONTENT_TYPE', '').startswith('multipart')
                            or request.META.get('HTTP_CONTENT_RANGE', False))
        try:
            # You cannot access body after reading from request's data stream
            body = request.body if not is_binary_upload else ''
        except Exception:
            body = "--can't-be-loggged--"

        user = None
        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                user = request.user
        # TODO: support DRF user

        resolver = getattr(request, 'resolver_match')

        self.create(
            url=request.get_full_path()[:200],
            method=request.method,
            status_code=response.status_code,
            in_headers=utils.pretty_headers_request(request),
            out_headers=utils.pretty_headers_response(response),
            ip=utils.get_client_ip(request),
            request=body,
            response=response.content,
            data=utils.pretty_data(request),
            app_name=(resolver.app_name or '') if resolver else '',
            user=user,
        )


class Entry(models.Model):
    url = models.URLField(db_index=True)
    method = models.CharField(max_length=6, db_index=True)
    status_code = models.IntegerField('Code')
    in_headers = models.TextField(blank=True)
    out_headers = models.TextField(blank=True)
    ip = models.GenericIPAddressField(blank=True, null=True, db_index=True)
    request = models.TextField(blank=True)
    response = models.TextField(blank=True)
    data = models.TextField(blank=True)
    app_name = models.CharField(max_length=15, blank=True, db_index=True)
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', User), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = LogManager()

    def __repr__(self):
        return '<Log %(status_code)s "%(url)s">' % {
            'status_code': self.status_code,
            'url': self.url
        }

    class Meta:
        verbose_name = _(u'log entry')
        verbose_name_plural = _(u'log entry')
