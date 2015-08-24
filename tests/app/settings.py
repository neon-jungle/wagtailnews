import sys
import os
from django.conf import global_settings


def env(name, default=None):
    if sys.version_info < (3,):
        return os.environ.get(name, failobj=default)
    else:
        return os.environ.get(name, default=default)


INSTALLED_APPS = [
    'wagtailnews',
    'tests.app',

    'taggit',
    'compressor',
    'modelcluster',

    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtailusers',
    'wagtail.wagtailsites',
    'wagtail.wagtailsnippets',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

SECRET_KEY = 'not a secret'

ROOT_URLCONF = 'tests.app.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': env('DATABASE_NAME', 'test.sqlite3'),
    },
}

WAGTAIL_SITE_NAME = 'Wagtail News'

DEBUG = True

USE_TZ = True
TIME_ZONE = 'Australia/Hobart'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.wagtailcore.middleware.SiteMiddleware',
]


TEMPLATE_CONTEXT_PROCESSORS = list(global_settings.TEMPLATE_CONTEXT_PROCESSORS) + [
    'django.core.context_processors.request',
]

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
STATIC_URL = '/static/'
