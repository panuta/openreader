from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'auth_login', name='auth_login'),

    url(r'^accounts/welcome/$', 'view_user_welcome', name='view_user_welcome'),

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^my/account/$', 'view_my_account', name='view_my_account'),
    url(r'^my/account/change_password/$', 'change_my_account_password', name='change_my_account_password'),

    # Organization

    url(r'^org/(?P<organization_slug>\w+)/profile/$', 'view_organization_profile', name='view_organization_profile'),
    url(r'^org/(?P<organization_slug>\w+)/profile/edit/$', 'edit_organization_profile', name='edit_organization_profile'),
    
    url(r'^org/(?P<organization_slug>\w+)/manage/users/$', 'view_organization_users', name='view_organization_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invite/$', 'invite_organization_user', name='invite_organization_user'),
    url(r'^invitation/(?P<invitation_id>\d+)/resend/$', 'resend_user_invitation', name='resend_user_invitation'),
    url(r'^invitation/(?P<invitation_id>\d+)/cancel/$', 'cancel_user_invitation', name='cancel_user_invitation'),
    url(r'^invitation/(?P<invitation_key>\w+)/$', 'claim_user_invitation', name='claim_user_invitation'),
    url(r'^user/(?P<organization_user_id>\d+)/edit/$', 'edit_organization_user', name='edit_organization_user'),
    url(r'^user/(?P<organization_user_id>\d+)/remove/$', 'remove_organization_user', name='remove_organization_user'),

    url(r'^org/(?P<organization_slug>\w+)/manage/roles/$', 'view_organization_roles', name='view_organization_roles'),
    url(r'^org/(?P<organization_slug>\w+)/manage/roles/add/$', 'add_organization_role', name='add_organization_role'),
    url(r'^role/(?P<organization_role_id>\d+)/edit/$', 'edit_organization_role', name='edit_organization_role'),
    url(r'^role/(?P<organization_role_id>\d+)/remove/$', 'remove_organization_role', name='remove_organization_role'),
    

    url(r'^org/(?P<organization_slug>\w+)/manage/billing/$', 'view_organization_billing', name='view_organization_billing'),
)