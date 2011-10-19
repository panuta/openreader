from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('', include('openreader.accounts.urls')),
    url('', include('openreader.homepage.urls')),
    url('', include('openreader.publication.urls')),

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
)
