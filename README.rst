=============================
django-httplog
=============================

.. image:: https://badge.fury.io/py/django-httplog.png
    :target: http://badge.fury.io/py/django-httplog

.. image:: https://travis-ci.org/futurecolors/django-httplog.png?branch=master
    :target: https://travis-ci.org/futurecolors/django-httplog

.. image:: https://coveralls.io/repos/futurecolors/django-httplog/badge.png?branch=master
    :target: https://coveralls.io/r/futurecolors/django-httplog?branch=master


Very simple http request-response log in database for debugging APIs.

I've used it to debug small API for Django, built with DRF.

.. warning::

This is not for production systems, if you want to handle reasonable amount of
data, please use `logstash`_, `Runscope`_, `django-request`_ or similar solutions.
Each one has it's own focus.

..  _logstash: http://logstash.net/
..  _runscope: https://www.runscope.com/
..  _django-request: https://github.com/kylef/django-request


Quickstart
----------

Install django-httplog::

    pip install django-httplog

Add 'httplog' to INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'httplog',
        ...
    )

Make sure user model is available either via settings.AUTH_USER_MODEL or
``django.contrib.auth`` is installed too.

Launch  ``manage.py syncdb`` or ``manage.py migrate``

Add middleware::

    MIDDLEWARE_CLASSES = (
        ...
        'httplog.middleware.RequestResponseLoggingMiddleware',
        ...
    )

Add viewnames to log, or app_name (from ulrs.py) to log::

    HTTPLOG_URLNAMES = ['urlname1', 'urlname_x']
    HTTPLOG_APPS = ['my_super_app_name']

By default, nothing is logged.

Features
--------

* TODO: support DRF user
