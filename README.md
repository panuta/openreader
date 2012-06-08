OpenReader Developer Document
=============

How to switch settings environment
-------------
For development
* Unset ```DJANGO_SETTINGS_MODULE``` variable, Django will use settings.development by default

For production
* Set ```DJANGO_SETTINGS_MODULE``` to ```openreader.settings.production```

User accounts and permissions
-------------

User
Group

Necessary Libraries
=============
- psycopg2
- PIL
- django-private_files (included)
- django-storages (included)
- django-pagination
- django-debug_toolbar
