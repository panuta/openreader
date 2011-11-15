from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url('', include('openreader.accounts.urls')),
    url('', include('openreader.homepage.urls')),
    url('', include('openreader.publication.urls')),

    url('', include('openreader.publication.book.urls')),
    url('', include('openreader.publication.magazine.urls')),

    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/accounts/login/'}, name="auth_logout"),
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )