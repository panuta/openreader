from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',

    url('', include('accounts.urls')),
    url('', include('presentation.urls')),
    url('', include('presentation.urls_ajax')),

    url('api/', include('api.urls')),
    url('management/', include('management.urls')),
    url('management/', include('management.urls_ajax')),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page':'/accounts/login/'},name='auth_logout'),
    url(r'^accounts/password_reset/$', 'django.contrib.auth.views.password_reset', name='auth_password_reset'),
    url(r'^accounts/password_reset/done/$', 'django.contrib.auth.views.password_reset_done', name='auth_password_reset_done'),
    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', name='auth_password_reset_confirm'),
    url(r'^accounts/reset/done/$', 'django.contrib.auth.views.password_reset_complete', name='auth_password_reset_complete'),

    url(r'^language/', 'common.views.set_language', name='set_lang'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {}),

    url(r'^org/(?P<organization_slug>\w+)/$', 'presentation.views.view_organization_front', name='view_organization_front'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^private_files/', include('private_files.urls')),

    url(r'^$', 'accounts.views.view_user_home', name='view_user_home'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
