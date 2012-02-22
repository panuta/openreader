from settings import *
#Alter or add production specific variables

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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN_NAME = 'localhost'

EMAIL_FOR_USER_PUBLISHER_INVITATION = 'noreply@' + EMAIL_DOMAIN_NAME

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'username@gmail.com'
# EMAIL_HOST_PASSWORD = 'password'
# EMAIL_PORT = 587

SECRET_KEY = '*r3geszk-gvq8cl==g1_o^2ivx&wx6vuz*osszca2mtivv=u*@'

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
            'filename': '/web/openreader/logs/openreader.log',
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