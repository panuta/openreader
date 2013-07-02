from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('presentation.views',

    # USER ACCOUNT #####################################################################################################

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^my/account/change_password/$', 'change_my_account_password', name='change_my_account_password'),

    # Manage Organization

    url(r'^org/(?P<organization_slug>\w+)/profile/$', 'view_organization_profile', name='view_organization_profile'),

    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/$', 'view_organization_users_groups', name='view_organization_users_groups'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/#users', RedirectView.as_view(), name='view_organization_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users-groups/#groups$', RedirectView.as_view(), name='view_organization_groups'),

    url(r'^user/(?P<organization_user_id>\d+)/edit/$', 'edit_organization_user', name='edit_organization_user'),

    # Manage User
    url(r'^org/(?P<organization_slug>\w+)/manage/users/add/$', 'add_organization_user', name='add_organization_user'),

    # User Invitation
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invited/$', 'view_organization_invited_users', name='view_organization_invited_users'),
    url(r'^org/(?P<organization_slug>\w+)/manage/users/invite/$', 'invite_organization_user', name='invite_organization_user'),
    url(r'^invitation/(?P<invitation_id>\d+)/edit/$', 'edit_user_invitation', name='edit_user_invitation'),
    url(r'^invitation/(?P<invitation_key>\w+)/$', 'claim_user_invitation', name='claim_user_invitation'),

    # Group
    url(r'^org/(?P<organization_slug>\w+)/manage/group/add/$', 'add_organization_group', name='add_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/edit/$', 'edit_organization_group', name='edit_organization_group'),
    url(r'^group/(?P<organization_group_id>\d+)/members/$', 'view_organization_group_members', name='view_organization_group_members'),

    # Banner
    url(r'^org/(?P<organization_slug>\w+)/banners/$', 'organization_banners', name='organization_banners'),
    url(r'^org/(?P<organization_slug>\w+)/banner/create/$', 'organization_banner_create', name='organization_banner_create'),
    url(r'^org/(?P<organization_slug>\w+)/banner/(?P<banner_id>\d+)/edit/$', 'organization_banner_edit', name='organization_banner_edit'),
    url(r'^org/(?P<organization_slug>\w+)/banner/(?P<banner_id>\d+)/delete/$', 'organization_banner_delete', name='organization_banner_delete'),

    # Knowledge
    url(r'^org/(?P<organization_slug>\w+)/knowledge/$', 'organization_knowledge', name='organization_knowledge'),
    url(r'^org/(?P<organization_slug>\w+)/knowledge/create/$', 'organization_knowledge_create', name='organization_knowledge_create'),
    url(r'^org/(?P<organization_slug>\w+)/knowledge/(?P<knowledge_id>\d+)/edit/$', 'organization_knowledge_edit', name='organization_knowledge_edit'),
    url(r'^org/(?P<organization_slug>\w+)/knowledge/(?P<knowledge_id>\d+)/delete/$', 'organization_knowledge_delete', name='organization_knowledge_delete'),

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