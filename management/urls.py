from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('management.views',
    url(r'^$', 'manage_front', name='manage_front'),
    url(r'^organizations/$', 'manage_organizations', name='manage_organizations'),
    url(r'^organization/create/$', 'create_organization', name='manage.create_organization'),

    url(r'^organization/invitation/(?P<invitation_key>\w+)/$', 'claim_organization_invitation', name='claim_organization_invitation'),
    url(r'^organization/invitation/(?P<invitation_id>\w+)/edit/$', 'edit_organization_invitation', name='edit_organization_invitation'),
    url(r'^organizations/invited/$', 'view_organizations_invited', name='view_organizations_invited'),

    url(r'^organization/(?P<organization_slug>\w+)/edit/$', 'edit_organization', name='edit_organization'),

    url(r'^banners/$', 'manage_banners', name='manage_banners'),
    url(r'^banner/create/$', 'manage_banner_create', name='manage_banner_create'),
    url(r'^banner/(?P<banner_id>\d+)/delete/$', 'manage_banner_delete', name='manage_banner_delete'),

    url(r'^knowledge/$', 'manage_knowledge', name='manage_knowledge'),
    url(r'^knowledge/create/$', 'manage_knowledge_create', name='manage_knowledge_create'),
    url(r'^knowledge/(?P<knowledge_id>\d+)/delete/$', 'manage_knowledge_delete', name='manage_knowledge_delete'),
)
