from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('management.views_ajax',
    
    url(r'^invitation/(?P<invitation_id>\d+)/resend/$', 'ajax_resend_organization_invitation', name='ajax_resend_organization_invitation'),
    url(r'^invitation/(?P<invitation_id>\d+)/cancel/$', 'ajax_cancel_organization_invitation', name='ajax_cancel_organization_invitation'),

    url(r'^ajax/banner/(?P<banner_id>\d+)/delete/$', 'ajax_manage_banner_delete', name="ajax_manage_banner_delete"),
    url(r'^ajax/knowledge/(?P<knowledge_id>\d+)/delete/$', 'ajax_manage_knowledge_delete', name="ajax_manage_knowledge_delete"),
)
