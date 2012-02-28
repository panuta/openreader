from settings import *
#Alter or add development specific variables

DEBUG = True

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

SECRET_KEY = 'THIS IS A SECRET KEY' # Real secret key is in production.py

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
            'filename': MEDIA_ROOT + '/logs/openreader.log',
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