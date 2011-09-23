from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('openreader.membership.urls')),
    url(r'^', include('openreader.publication.urls')),
    
    url(r'^accounts/', include('registration.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
