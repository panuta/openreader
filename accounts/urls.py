from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'auth_login', name='auth_login'),

    url(r'^accounts/welcome/$', 'view_user_welcome', name='view_user_welcome'),

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^my/account/$', 'view_my_account', name='view_my_account'),
    url(r'^my/account/change_password/$', 'change_my_account_password', name='change_my_account_password'),

    # Organization

    url(r'^org/(?P<organization_slug>\w+)/profile/$', 'view_organization_profile', name='view_organization_profile'),
    
    url(r'^org/(?P<organization_slug>\w+)/manage/users/$', 'view_organization_users', name='view_organization_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invited/$', 'view_organization_invited_users', name='view_organization_invited_users'),

    url(r'^org/(?P<organization_slug>\w+)/manage/users/invite/$', 'invite_organization_user', name='invite_organization_user'),

    url(r'^invitation/(?P<invitation_id>\d+)/edit/$', 'edit_user_invitation', name='edit_user_invitation'),
    url(r'^invitation/(?P<invitation_key>\w+)/$', 'claim_user_invitation', name='claim_user_invitation'),
    url(r'^invitation/(?P<invitation_id>\d+)/resend/$', 'ajax_resend_user_invitation', name='ajax_resend_user_invitation'),
    url(r'^invitation/(?P<invitation_id>\d+)/cancel/$', 'ajax_cancel_user_invitation', name='ajax_cancel_user_invitation'),

    url(r'^user/(?P<organization_user_id>\d+)/edit/$', 'edit_organization_user', name='edit_organization_user'),
    url(r'^user/(?P<organization_user_id>\d+)/remove/$', 'ajax_remove_organization_user', name='ajax_remove_organization_user'),

    url(r'^org/(?P<organization_slug>\w+)/manage/groups/$', 'view_organization_groups', name='view_organization_groups'),
    url(r'^org/(?P<organization_slug>\w+)/manage/groups/add/$', 'add_organization_group', name='add_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/edit/$', 'edit_organization_group', name='edit_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/remove/$', 'ajax_remove_organization_group', name='ajax_remove_organization_group'),
    
    # Ajax Services
    url(r'^ajax/(?P<organization_slug>\w+)/query/users/$', 'ajax_query_users', name='ajax_query_users'),
    url(r'^ajax/(?P<organization_slug>\w+)/query/groups/$', 'ajax_query_groups', name='ajax_query_groups'),
)