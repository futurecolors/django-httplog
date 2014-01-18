#!/usr/bin/env python
# coding: utf-8
import sys
import httplog

try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    from distutils.core import setup

version = httplog.__version__

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-httplog',
    version=version,
    description="""Very simple http request-response log in database for debugging APIs.""",
    long_description=readme + '\n\n' + history,
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    url='https://github.com/coagulant/django-httplog',
    packages=[
        'httplog',
    ],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords='django-httplog',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
