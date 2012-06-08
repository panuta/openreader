import os
import sys

path = '/web/sites/openreader'
if path not in sys.path:
    sys.path.append(path)

path = '/web/sites/openreader/openreader'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'openreader.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
