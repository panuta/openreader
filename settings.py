import os
base_path = os.path.dirname(__file__)

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

SITE_ID = 1

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = os.path.join(base_path, 'media/')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

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
        'LOCATION': '/Users/apple/Projects/OpenReader/openreader-m2/openreader/media/cache',
    }
}

SECRET_KEY = '-73!l!kmu@h)1g!qjv4@9-l39*=mc_6tm^_+j)w0(tar_%twt5'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'openreader.urls'

TEMPLATE_DIRS = (
    os.path.join(base_path, 'templates'),
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
    
    'registration',
    #'private_files',

    'common',
    'membership',
    'publication',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

##### Open Reader Settings #####
PUBLICATION_ROOT = MEDIA_ROOT + 'publication/'
