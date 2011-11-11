from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.views',
    url(r'^dashboard/$', 'view_dashboard', name='view_dashboard'),

    url(r'^publisher/create/$', 'create_publisher', name='create_publisher'),
    url(r'^publisher/select/$', 'select_publisher', name='select_publisher'),

    # Upload
    url(r'^publisher/(?P<publisher_id>\d+)/upload/(?P<module_name>\w+)/$', 'upload_publication', name='upload_module_publication'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/$', 'upload_publication', name='upload_publication'),
    url(r'^publication/(?P<publication_id>\d+)/finishing_upload/$', 'finishing_upload_publication', name='finishing_upload_publication'),
    
    url(r'^get_upload_progress?.*$', 'get_upload_progress', name='get_upload_progress'),

    # Dashboard
    url(r'^publisher/(?P<publisher_id>\d+)/dashboard/$', 'view_publisher_dashboard', name='view_publisher_dashboard'),

    # Publisher Management
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/management/$', 'view_publisher_management', name='view_publisher_management'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/profile/$', 'view_publisher_profile', name='view_publisher_profile'),
    
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/shelfs/$', 'view_publisher_shelfs', name='view_publisher_shelfs'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/shelfs/create/$', 'view_publisher_shelfs_create', name='view_publisher_shelfs_create'),
    
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/users/$', 'view_publisher_users', name='view_publisher_users'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/users/add/$', 'view_publisher_users_add', name='view_publisher_users_add'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/billing/$', 'view_publisher_billing', name='view_publisher_billing'),

    # Publication
    url(r'^publication/(?P<publication_id>\d+)/$', 'view_publication', name='view_publication'),
    url(r'^publication/(?P<publication_id>\d+)/download/$', 'download_publication', name='download_publication'),
    url(r'^get/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'get_publication', name='get_publication'),

    url(r'^publication/(?P<publication_id>\d+)/edit/$', 'edit_publication', name='edit_publication'),
    url(r'^publication/(?P<publication_id>\d+)/edit/status/$', 'edit_publication_status', name='edit_publication_status'),

    url(r'^publication/(?P<publication_id>\d+)/set/published/$', 'set_publication_published', name='set_publication_published'),
    url(r'^publication/(?P<publication_id>\d+)/set/schedule/$', 'set_publication_schedule', name='set_publication_schedule'),
    url(r'^publication/(?P<publication_id>\d+)/set/cancel_schedule/$', 'set_publication_cancel_schedule', name='set_publication_cancel_schedule'),
    url(r'^publication/(?P<publication_id>\d+)/set/revert/$', 'set_publication_revert', name='set_publication_revert'),

)
