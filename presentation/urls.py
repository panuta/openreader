from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('presentation.views',

    # USER ACCOUNT #####################################################################################################

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^my/account/change_password/$', 'change_my_account_password', name='change_my_account_password'),

    # ORGANIZATION REGISTER #####################################################################################################
    url(r'^org/plan/$', 'plan_organization', name='plan_organization'),
    url(r'^org/register/$', 'register_organization', name='register_organization'),
    url(r'^org/register/done/$', 'register_organization_done', name='register_organization_done'),

    # Manage Organization

    url(r'^org/(?P<organization_slug>\w+)/profile/$', 'view_organization_profile', name='view_organization_profile'),
    url(r'^org/(?P<organization_slug>\w+)/remove/$', 'remove_organization', name='remove_organization'),

    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/$', 'view_organization_users_groups', name='view_organization_users_groups'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/#users', RedirectView.as_view(), name='view_organization_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/#groups$', RedirectView.as_view(), name='view_organization_groups'),

    url(r'^user/(?P<organization_user_id>\d+)/edit/$', 'edit_organization_user', name='edit_organization_user'),

    # Manage User
    url(r'^org/(?P<organization_slug>\w+)/manage/users/add/$', 'add_organization_user', name='add_organization_user'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users/summarize/$', 'summarize_organization_users', name='summarize_organization_users'),

    # Payment
    url(r'^org/(?P<organization_slug>\w+)/payment/$', 'organization_make_payment', name='organization_make_payment'),
    url(r'^org/payment/paypal/notify/$', 'organization_notify_from_paypal', name='organization_notify_from_paypal'),
    url(r'^org/payment/paypal/return/$', 'organization_return_from_paypal', name='organization_return_from_paypal'),

    # User Invitation
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invited/$', 'view_organization_invited_users', name='view_organization_invited_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invite/$', 'invite_organization_user', name='invite_organization_user'),
    url(r'^invitation/(?P<invitation_id>\d+)/edit/$', 'edit_user_invitation', name='edit_user_invitation'),
    url(r'^invitation/(?P<invitation_key>\w+)/$', 'claim_user_invitation', name='claim_user_invitation'),

    # Group
    url(r'^org/(?P<organization_slug>\w+)/manage/group/add/$', 'add_organization_group', name='add_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/edit/$', 'edit_organization_group', name='edit_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/members/$', 'view_organization_group_members', name='view_organization_group_members'),

    # DOCUMENT #########################################################################################################

    url(r'^org/(?P<organization_slug>\w+)/documents/$', 'view_documents', name='view_documents'),
    url(r'^org/(?P<organization_slug>\w+)/documents/shelf/(?P<shelf_id>\d+)/$', 'view_documents_by_shelf', name='view_documents_by_shelf'),

    url(r'^org/(?P<organization_slug>\w+)/shelf/create/$', 'create_document_shelf', name='create_document_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/shelf/(?P<shelf_id>\d+)/edit/$', 'edit_document_shelf', name='edit_document_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/shelf/(?P<shelf_id>\d+)/delete/$', 'delete_document_shelf', name='delete_document_shelf'),

    # Publication
    url(r'^publication/(?P<publication_uid>[a-zA-Z0-9\-]+)/download/$', 'download_publication', name='download_publication'),
    #url(r'^publication/(?P<publication_uid>[a-zA-Z0-9\-]+)/replace/$', 'replace_publication', name='replace_publication'),

)