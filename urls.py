from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

if settings.SITE_TYPE == 'document':
    urlpatterns = patterns('',
        url(r'^org/(?P<organization_slug>\w+)/$', 'document.views.view_organization_front', name='view_organization_front'),
        url('', include('openreader.document.urls')),
    )

if settings.SITE_TYPE == 'publisher':
    urlpatterns = patterns('',
        url(r'^org/(?P<organization_slug>\w+)/$', 'publisher.views.view_organization_front', name='view_organization_front'),
        url('', include('openreader.publisher.urls')),
   )

urlpatterns += patterns('',
    url('api/', include('openreader.api.urls')),

    url('', include('openreader.accounts.urls')),
    #url('', include('openreader.homepage.urls')),
    url('', include('openreader.publication.urls')),
    url('management/', include('openreader.management.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/accounts/login/'},name='auth_logout'),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', name='auth_password_reset'),
    url(r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='auth_password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', name='auth_password_reset_confirm'),
    url(r'^accounts/reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='auth_password_reset_complete'),

    url(r'^$', 'accounts.views.view_user_home', name='view_user_home'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )