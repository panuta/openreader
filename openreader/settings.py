# -*- encoding: utf-8 -*-

import os
base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir)

from django.conf import global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

WEBSITE_NAME = 'OpenReader'
WEBSITE_DOMAIN = 'https://127.0.0.1:9001'

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

ADMINS = ()
MANAGERS = ADMINS

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('th', gettext('Thai')),
)

LOCALE_PATHS = (
    os.path.join(base_path, 'locale'),
)

SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True

# SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

MEDIA_ROOT = os.path.join(base_path, 'media/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(base_path, 'sitestatic/')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(base_path, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(base_path, 'media/cache/'),
    }
}

SECRET_KEY = 'THIS IS A SECRET KEY'

AUTH_PROFILE_MODULE = 'domain.UserProfile'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'openreader.backends.EmailAuthenticationBackend',
    'openreader.backends.InvitationAuthenticationBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

FILE_UPLOAD_HANDLERS = ('openreader.handlers.UploadProgressCachedHandler', ) + global_settings.FILE_UPLOAD_HANDLERS

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

ROOT_URLCONF = 'openreader.urls'
WSGI_APPLICATION = 'openreader.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(base_path, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'openreader.context.constants',
)

MIDDLEWARE_CLASSES = (
    'openreader.middleware.AJAXSimpleExceptionResponse',
    'openreader.http.Http403Middleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
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
    'djkombu',
    'paypal.standard.pdt',
    
    'accounts',
    'domain',
    'presentation',

    'api',
    'common',
    'management',
)

OPENREADER_LOGGER = 'openreader'

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

# Email

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN_NAME = 'localhost'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'application.testbed@gmail.com'
EMAIL_HOST_PASSWORD = 'opendreamqwer'
EMAIL_PORT = 587

EMAIL_ADDRESS_NO_REPLY = 'noreply@' + EMAIL_DOMAIN_NAME

########## Django Debug Toolbar ##########

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    }

########## Django Celery ##########

import djcelery
djcelery.setup_loader()

# BROKER_URL = "redis://localhost:6379/0"

# BROKER_HOST = "localhost"
# BROKER_PORT = 5672
# BROKER_USER = "guest"
# BROKER_PASSWORD = "guest"
# BROKER_VHOST = "/"

# BROKER_TRANSPORT = 'redis'

BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
#celery
BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

from datetime import timedelta
from domain import tasks

CELERYBEAT_SCHEDULE = {
    'decide-on-first-month-everydays': {
        'task': 'tasks.send_notification_email_to_decide_on_first_month',
        'schedule': timedelta(days=1),
    },
    # 'decide-on-first-month-test-every-10-seconds': {
    #     'task': 'tasks.send_notification_email_to_decide_on_first_month',
    #     'schedule': timedelta(seconds=30),
    # },
}

########## Django Private Files ##########

FILE_PROTECTION_METHOD = 'basic'

########## Django Pagination ##########

PAGINATION_DEFAULT_PAGINATION = 50

########## Open Reader Settings ##########

PUBLICATION_PREFIX = '/publication'
PUBLICATION_ROOT = MEDIA_ROOT + PUBLICATION_PREFIX

MAX_PUBLICATION_FILE_SIZE = 300000000 # 300mb
MAX_PUBLICATION_FILE_SIZE_TEXT = '300 เมกะไบต์'

# Publication Download

DOWNLOAD_LINK_EXPIRE_IN = 180 # Minutes

# Thumbnail
THUMBNAIL_ROOT = PUBLICATION_ROOT + '/thumbnails'
THUMBNAIL_TEMP_ROOT = MEDIA_ROOT + '/thumbnails_temp' # Use when generating thumbnails
THUMBNAIL_URL = MEDIA_URL + '/publication/thumbnails'

THUMBNAIL_SIZES = (
    ('small', (70, 85)),
    ('large', (200, 250)),
)

# Set to False if server can generate thumbnail 99%
THUMBNAIL_REGENERATE = True

# Shelf Icons
DEFAULT_SHELF_ICON = 'basic1-006'
SHELF_ICONS = ['basic1-006', 'basic1-041', 'basic1-049', 'basic1-052', 'basic1-054', 'basic1-106', 'basic1-129', 'basic2-001', 'basic2-011', 'basic2-018', 'basic2-057', 'basic2-092', 'basic2-096', 'basic2-102', 'basic2-106', 'basic2-114', 'basic2-117', 'basic2-142', 'basic2-197', 'basic2-238', 'basic2-253', 'basic2-256', 'basic2-258', 'basic2-267', 'basic2-268']

# PAYPAL
PAYPAL_IDENTITY_TOKEN = 'hRc3sUDb6s5VPiY7l79fbN2qKTYf0Sk8Y1LIwosSidLUFXYDJAlpyx58xEO'
PAYPAL_RECEIVER_EMAIL = 'sell_1350615922_biz@hotmail.com'

#######################################################

try:
    from settings_local import *
except ImportError:
    pass
