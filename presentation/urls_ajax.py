from django.conf.urls import patterns, url

urlpatterns = patterns('presentation.views_ajax',

    # USER ACCOUNT #####################################################################################################

    url(r'^invitation/(?P<invitation_id>\d+)/resend/$', 'ajax_resend_user_invitation', name='ajax_resend_user_invitation'),
    url(r'^invitation/(?P<invitation_id>\d+)/cancel/$', 'ajax_cancel_user_invitation', name='ajax_cancel_user_invitation'),

    url(r'^user/(?P<organization_user_id>\d+)/remove/$', 'ajax_remove_organization_user', name='ajax_remove_organization_user'),
    url(r'^group/(?P<organization_group_id>\d+)/remove/$', 'ajax_remove_organization_group', name='ajax_remove_organization_group'),

    url(r'^ajax/(?P<organization_slug>\w+)/query/users/$', 'ajax_query_users', name='ajax_query_users'),
    url(r'^ajax/(?P<organization_slug>\w+)/query/groups/$', 'ajax_query_groups', name='ajax_query_groups'),

    # DOCUMENT #########################################################################################################

    url(r'^ajax/(?P<organization_slug>\w+)/publication/tag/add/$', 'ajax_add_publications_tag', name='ajax_add_publications_tag'),
    url(r'^ajax/(?P<organization_slug>\w+)/publication/edit/$', 'ajax_edit_publication', name='ajax_edit_publication'),
    url(r'^ajax/(?P<organization_slug>\w+)/publication/delete/$', 'ajax_delete_publication', name='ajax_delete_publication'),
    url(r'^ajax/(?P<organization_slug>\w+)/query/publication-tags/$', 'ajax_query_publication_tags', name='ajax_query_publication_tags'),

)