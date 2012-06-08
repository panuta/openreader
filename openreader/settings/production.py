# -*- encoding: utf-8 -*-

from openreader.settings import *

DEBUG = False
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

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'username@gmail.com'
# EMAIL_HOST_PASSWORD = 'password'
# EMAIL_PORT = 587

SECRET_KEY = '*r3geszk-gvq8cl==g1_o^2ivx&wx6vuz*osszca2mtivv=u*@'

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
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'pagination',
    'private_files',
    'djcelery',

    'accounts',
    'api',
    'common',
    'document',
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
            'level': 'ERROR'
        },
    }
}
