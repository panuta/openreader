# -*- encoding: utf-8 -*-

import os
base_path = os.path.dirname(__file__)

from django.conf import global_settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Panu Tangchalermkul', 'panuta@gmail.com'),
)

MANAGERS = ADMINS

# Contact address in welcome page (For user who has no publisher record)
WELCOME_CONTACT_EMAIL = 'welcome@openreader.com'

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
WEBSITE_DOMAIN = 'http://127.0.0.1:8000/'
WEBSITE_HOST = '127.0.0.1:8000' # Use for system email address

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(base_path, 'media/')
MEDIA_URL = '/media/'

# DEFAULT_FILE_STORAGE = 'mystorages.backends.sftpstorage.SFTPStorage'

STATIC_ROOT = os.path.join(base_path, 'sitestatic/')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

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

AUTH_PROFILE_MODULE = 'document.UserProfile'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'backends.EmailAuthenticationBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    #'django.contrib.auth.backends.ModelBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'username@gmail.com'
# EMAIL_HOST_PASSWORD = 'password'
# EMAIL_PORT = 587

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*r3geszk-gvq8cl==g1_o^2ivx&wx6vuz*osszca2mtivv=u*@'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'middleware.AJAXSimpleExceptionResponse',
    'http.Http403Middleware',
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

ROOT_URLCONF = 'urls'

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
    'context.constants',
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
    'storages',
    'pagination',
    'debug_toolbar',

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
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/tmp/openreader.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'openreader': {
            'handlers': ['file'],
            'level': 'DEBUG'
        },
    }
}

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS':False}

########## Django Private Files ##########

FILE_PROTECTION_METHOD = 'basic'

########## Django Storages ##########

SFTP_STORAGE_HOST = '172.16.204.129'
SFTP_STORAGE_ROOT = '/web/sites/openreader/files/'
SFTP_STORAGE_PARAMS = {'username':'root', 'password':'panuta'}

########## Django Compressor ##########
COMPRESS_ENABLED = True

COMPRESS_PRECOMPILERS = (
    ('text/less', os.path.join(base_path, 'misc/less/lessc') + ' {infile} {outfile}'),
    # ('text/less', 'lessc {infile} {outfile}'),
)

########## Django Pagination ##########

PAGINATION_DEFAULT_PAGINATION = 50

########## Open Reader Settings ##########
OPENREADER_LOGGER = 'openreader'

PUBLICATION_ROOT = MEDIA_ROOT + 'publication/'
MAX_PUBLICATION_FILE_SIZE = 300000000 # 300mb
MAX_PUBLICATION_FILE_SIZE_TEXT = '300 เมกะไบต์'

EMAIL_FOR_USER_PUBLISHER_INVITATION = 'noreply@' + WEBSITE_HOST

# Thumbnail

THUMBNAIL_GENERATORS = (
    'thumbnail_generators.ImageThumbnailGenerator',
    'thumbnail_generators.PDFThumbnailGenerator',
    'thumbnail_generators.VideoThumbnailGenerator',
)

THUMBNAIL_SIZES = (
    ('small', (70, 85)),
    ('large', (200, 250)),
)

# Set to False if server can generate thumbnail 99%
THUMBNAIL_REGENERATE = True

# Shelf Icons
DEFAULT_SHELF_ICON = 'basic2-092'
SHELF_ICONS = ['basic1-006','basic1-041','basic1-060','basic1-107','basic1-122','basic1-129','basic2-001','basic2-092','basic2-143','basic2-182','basic2-196','basic2-215','basic2-241','basic2-253','basic2-256']

#######################################################