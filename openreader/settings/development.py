# -*- encoding: utf-8 -*-

from openreader.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Panu Tangchalermkul', 'panuta@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openreader',
        'USER': 'openreader',
        'PASSWORD': 'openreader',
        'HOST': '',
        'PORT': '',
    }
}

WEBSITE_DOMAIN = 'http://127.0.0.1:8000'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN_NAME = 'localhost'

EMAIL_FOR_USER_PUBLISHER_INVITATION = 'noreply@' + EMAIL_DOMAIN_NAME

SECRET_KEY = 'THIS IS A SECRET KEY'

MIDDLEWARE_CLASSES = (
    'openreader.middleware.AJAXSimpleExceptionResponse',
    'openreader.http.Http403Middleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'pagination.middleware.PaginationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'private_files',
    
    'pagination',
    'debug_toolbar',
    'djcelery',

    'accounts',
    'domain',
    'presentation',

    'api',
    'common',
    'management',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': MEDIA_ROOT + '/openreader.log',
            'formatter':'default'
        }
    },
    'loggers': {
        OPENREADER_LOGGER: {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
    }
}

########## Django Debug Toolbar ##########

DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS':False}