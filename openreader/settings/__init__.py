# -*- encoding: utf-8 -*-

import os
base_path = os.path.join(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir), os.path.pardir)

from django.conf import global_settings

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

WEBSITE_NAME = 'OpenReader'
WEBSITE_DOMAIN = 'http://127.0.0.1:8000'

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(base_path, 'media')
MEDIA_URL = '/media'

# DEFAULT_FILE_STORAGE = 'mystorages.backends.sftpstorage.SFTPStorage'

STATIC_ROOT = os.path.join(base_path, 'sitestatic/')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static-admin/'

STATICFILES_DIRS = (
    os.path.join(base_path, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(base_path, 'media/cache/'),
    }
}

AUTH_PROFILE_MODULE = 'accounts.UserProfile'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'openreader.backends.EmailAuthenticationBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'openreader.http.Http403Middleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',

    'pagination.middleware.PaginationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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

FILE_UPLOAD_HANDLERS = ('handlers.UploadProgressCachedHandler', ) + global_settings.FILE_UPLOAD_HANDLERS

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
    'djcelery',
    'debug_toolbar',

    'accounts',
    'api',
    'common',
    'document',
    'management',
)

OPENREADER_LOGGER = 'openreader'

########## Django Debug Toolbar ##########

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

########## Django Celery ##########

import djcelery
djcelery.setup_loader()

BROKER_URL = "redis://localhost:6379/0"

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

BROKER_TRANSPORT = 'redis'


########## Django Private Files ##########

FILE_PROTECTION_METHOD = 'basic'

########## Django Compressor ##########
COMPRESS_ENABLED = True

COMPRESS_PRECOMPILERS = (
    ('text/less', os.path.join(base_path, 'misc/less/lessc') + ' {infile} {outfile}'),
    # ('text/less', 'lessc {infile} {outfile}'),
)

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
THUMBNAIL_URL = '/thumbnails'

THUMBNAIL_SIZES = (
    ('small', (70, 85)),
    ('large', (200, 250)),
)

# Set to False if server can generate thumbnail 99%
THUMBNAIL_REGENERATE = True

# Shelf Icons
DEFAULT_SHELF_ICON = 'basic1-006'
SHELF_ICONS = ['basic1-006', 'basic1-041', 'basic1-049', 'basic1-052', 'basic1-054', 'basic1-106', 'basic1-129', 'basic2-001', 'basic2-011', 'basic2-018', 'basic2-057', 'basic2-092', 'basic2-096', 'basic2-102', 'basic2-106', 'basic2-114', 'basic2-117', 'basic2-142', 'basic2-197', 'basic2-238', 'basic2-253', 'basic2-256', 'basic2-258', 'basic2-267', 'basic2-268']

#######################################################
