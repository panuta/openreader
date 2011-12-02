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
ADMIN_MEDIA_PREFIX = '/static/admin/'

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
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(base_path, 'media/cache/'),
    }
}

AUTH_PROFILE_MODULE = 'accounts.UserProfile'
LOGIN_REDIRECT_URL = '/dashboard/'

AUTHENTICATION_BACKENDS = (
    'openreader.backends.EmailAuthenticationBackend',
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
    'openreader.middleware.AJAXSimpleExceptionResponse',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'openreader.urls'

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
    'openreader.context_processors.constants',
    )

FILE_UPLOAD_HANDLERS = ('openreader.handlers.UploadProgressCachedHandler', ) + global_settings.FILE_UPLOAD_HANDLERS

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'private_files',
    'mystorages',
    'pagination',

    'openreader.accounts',
    'openreader.common',
    'openreader.publisher',
    'openreader.management',

    'openreader.publisher.book',
    'openreader.publisher.magazine',
    'openreader.publisher.file',
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
            'filename': 'openreader.log',
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

########## Django Private Files ##########

FILE_PROTECTION_METHOD = 'basic'

########## Django Storages ##########

SFTP_STORAGE_HOST = '172.16.204.129'
SFTP_STORAGE_ROOT = '/web/sites/openreader/files/'
SFTP_STORAGE_PARAMS = {'username':'root', 'password':'panuta'}

########## Django Pagination ##########

PAGINATION_DEFAULT_PAGINATION = 50

########## Open Reader Settings ##########

OPENREADER_LOGGER = 'openreader'

MAGAZINE_LOGO_ROOT = MEDIA_ROOT + 'magazine_logo/'
PUBLICATION_ROOT = MEDIA_ROOT + 'publication/'

EMAIL_FOR_USER_PUBLISHER_INVITATION = 'noreply@' + WEBSITE_HOST

# Thumbnail

THUMBNAIL_GENERATORS = (
    'openreader.thumbnail_generators.ImageThumbnailGenerator',
    'openreader.thumbnail_generators.PDFThumbnailGenerator',
    'openreader.thumbnail_generators.VideoThumbnailGenerator',
)

THUMBNAIL_SIZES = (
    ('small', (70, 85)),
    ('large', (200, 250)),
)

#######################################################