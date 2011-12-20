from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('management.views',
    url(r'^$', 'manage_front', name='manage_front'),
    url(r'^organizations/$', 'manage_organizations', name='manage_organizations'),
    url(r'^organizations/create/$', 'create_organization', name='manage.create_organization'),

    url(r'^organization/(?P<organization_slug>\d+)/$', 'manage_organization', name='manage_organization'),

)
