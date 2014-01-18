DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

SECRET_KEY = '_'
ROOT_URLCONF = 'test_app.urls'

INSTALLED_APPS = (
    'httplog',
    'test_app',
    'django.contrib.auth',
    'django.contrib.contenttypes',
)

MIDDLEWARE_CLASSES = ('httplog.middleware.RequestResponseLoggingMiddleware',)
HTTPLOG_URLNAMES = ['dummy']
HTTPLOG_APPS = ['auth']
