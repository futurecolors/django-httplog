# coding: utf-8
import datetime
import json
import os
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from httplog.middleware import RequestResponseLoggingMiddleware
from httplog.models import Entry


class TestMiddleware(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestResponseLoggingMiddleware()

    def test_simple_url_is_logged(self):
        request = self.factory.get('/api/simpleurl/')
        response = HttpResponse(status=200, content='<html>Hello</html>')
        result = self.middleware.process_response(
            request,
            response=response
        )
        assert result == response

        request = self.factory.get('/api/v2/')
        response = HttpResponse(status=200, content='<html>API</html>')
        result = self.middleware.process_response(
            request,
            response=response
        )
        assert result == response
        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 200 "/api/simpleurl/">',
                                                       '<Log 200 "/api/v2/">'], ordered=False)

    def test_other_urls_are_ignored(self):
        request = self.factory.get('/')
        self.middleware.process_response(
            request,
            response=HttpResponse(status=200, content='<html>Hello</html>')
        )
        self.assertQuerysetEqual(Entry.objects.all(), [])

    def test_get_url_is_recorded(self):
        request = self.factory.get('/login/?utm_source=spam')
        out_result = self.middleware.process_response(
            request,
            response=HttpResponse(status=200, content='<html>Hello</html>')
        )

        self.assertTrue(type(out_result) is HttpResponse)
        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 200 "/login/?utm_source=spam">'])
        log = Entry.objects.all()[0]

        self.assertEqual(log.url, '/login/?utm_source=spam')
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.status_code, 200)
        self.assertIn('SERVER_PROTOCOL: HTTP/1.1', log.in_headers)
        self.assertIn('Content-Type: text/html; charset=utf-8', log.out_headers)
        self.assertEqual(log.ip, '127.0.0.1')
        self.assertEqual(log.app_name, 'auth')
        self.assertEqual(log.request, '')
        self.assertEqual(log.response, '<html>Hello</html>')
        self.assertLessEqual(log.created_at, datetime.datetime.now())
        self.assertLessEqual(log.updated_at, datetime.datetime.now())

    def test_post_url_is_recorded(self):
        request = self.factory.post('/api/blog/post/create/', {'foo': u'бар'})
        self.middleware.process_response(
            request,
            response=HttpResponse(status=201, content='<html>Created</html>')
        )

        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 201 "/api/blog/post/create/">'])
        log = Entry.objects.all()[0]

        self.assertEqual(log.url, '/api/blog/post/create/')
        self.assertEqual(log.app_name, '')
        self.assertEqual(log.method, 'POST')
        self.assertEqual(log.status_code, 201)
        self.assertEqual(log.data, u'foo: бар')
        self.assertEqual(log.response, '<html>Created</html>')

    def test_put_url_is_recorded(self):
        request = self.factory.put('/api/json_handle/',
                                   content_type='application/json',
                                   data=json.dumps({'text': u'Привет, котики!',
                                                    'is_cool': None}))
        self.middleware.process_response(
            request,
            response=HttpResponse(status=404, content='<html>404</html>')
        )

        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 404 "/api/json_handle/">'])
        log = Entry.objects.all()[0]

        self.assertEqual(log.url, '/api/json_handle/')
        self.assertEqual(log.method, 'PUT')
        self.assertEqual(log.status_code, 404)
        assert set(log.data.split('\n')) == set((u"text: Привет, котики!", u"is_cool: None"))
        self.assertEqual(log.response, '<html>404</html>')

    def test_delete_url_is_recorded(self):
        request = self.factory.delete('/api/image/',)
        self.middleware.process_response(
            request,
            response=HttpResponse(status=204, content=u'Удалено')
        )

        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 204 "/api/image/">'])
        log = Entry.objects.all()[0]

        self.assertEqual(log.url, '/api/image/')
        self.assertEqual(log.method, 'DELETE')
        self.assertEqual(log.status_code, 204)
        self.assertEqual(log.response, u'Удалено')

    def test_binary_files_not_saved(self):
        with open(os.path.join('test_app', 'django-logo-positive.png'), 'rb') as fp:
            request = self.factory.post('/api/editor/42/image/', {'hello': 'dolly', 'file': fp})
        self.middleware.process_response(
            request,
            response=HttpResponse(status=200, content='')
        )
        log = Entry.objects.all()[0]
        self.assertEqual(log.request, '')
        assert set(log.data.split('\n')) == set((u"hello: dolly", u"file: django-logo-positive.png"))

    def test_stream_requests_dont_break_logging(self):
        request = self.factory.post('/api/dummy/',
                                    json.dumps({'hello': 'dolly'}),
                                    content_type='application/json')
        request._read_started = True  # emulating stream request
        self.middleware.process_response(
            request,
            response=HttpResponse(status=200, content='')
        )
        self.assertQuerysetEqual(Entry.objects.all(), ['<Log 200 "/api/dummy/">'])
        log = Entry.objects.all()[0]
        self.assertEqual(log.request, "--can't-be-loggged--")
        self.assertEqual(log.data, "")
