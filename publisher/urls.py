from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.views',

    url(r'^publisher/create/$', 'create_publisher', name='create_publisher'),

    # Dashboard
    url(r'^dashboard/$', 'view_dashboard', name='view_dashboard'),
    url(r'^publisher/(?P<publisher_id>\d+)/dashboard/$', 'view_publisher_dashboard', name='view_publisher_dashboard'),

    # Upload
    url(r'^publisher/(?P<publisher_id>\d+)/upload/(?P<module_name>\w+)/$', 'upload_publication', name='upload_module_publication'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/$', 'upload_publication', name='upload_publication'),
    url(r'^publication/(?P<publication_id>\d+)/finishing_upload/$', 'finishing_upload_publication', name='finishing_upload_publication'),
    
    url(r'^get_upload_progress?.*$', 'get_upload_progress', name='get_upload_progress'),

    # Publisher Management
    
    url(r'^publisher/(?P<publisher_id>\d+)/profile/$', 'view_publisher_profile', name='view_publisher_profile'),
    url(r'^publisher/(?P<publisher_id>\d+)/manage/$', 'edit_publisher_profile', name='edit_publisher_profile'),
    
    url(r'^publisher/(?P<publisher_id>\d+)/manage/shelfs/$', 'view_publisher_shelfs', name='view_publisher_shelfs'),
    url(r'^publisher/(?P<publisher_id>\d+)/manage/shelfs/create/$', 'create_publisher_shelf', name='create_publisher_shelf'),
    url(r'^publisher/shelf/(?P<publisher_shelf_id>\d+)/edit/$', 'edit_publisher_shelf', name='edit_publisher_shelf'),
    url(r'^publisher/shelf/(?P<publisher_shelf_id>\d+)/delete/$', 'delete_publisher_shelf', name='delete_publisher_shelf'),
    
    url(r'^publisher/(?P<publisher_id>\d+)/manage/users/$', 'view_publisher_users', name='view_publisher_users'),
    url(r'^publisher/(?P<publisher_id>\d+)/manage/users/invite/$', 'invite_publisher_user', name='invite_publisher_user'),
    url(r'^publisher/user/(?P<publisher_user_id>\d+)/edit/$', 'edit_publisher_user', name='edit_publisher_user'),
    url(r'^publisher/user/(?P<publisher_user_id>\d+)/remove/$', 'remove_publisher_user', name='remove_publisher_user'),

    url(r'^publisher/(?P<publisher_id>\d+)/manage/billing/$', 'view_publisher_billing', name='view_publisher_billing'),

    # Publication
    url(r'^publication/(?P<publication_id>\d+)/$', 'view_publication', name='view_publication'),
    url(r'^publication/(?P<publication_id>\d+)/download/$', 'download_publication', name='download_publication'),
    url(r'^get/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'get_publication', name='get_publication'),

    url(r'^publication/(?P<publication_id>\d+)/edit/$', 'edit_publication', name='edit_publication'),

    url(r'^publication/(?P<publication_id>\d+)/delete/uploading/$', 'delete_uploading_publication', name='delete_uploading_publication'),

    url(r'^publication/(?P<publication_id>\d+)/set/published/$', 'set_publication_published', name='set_publication_published'),
    url(r'^publication/(?P<publication_id>\d+)/set/schedule/$', 'set_publication_schedule', name='set_publication_schedule'),
    url(r'^publication/(?P<publication_id>\d+)/set/cancel_schedule/$', 'set_publication_cancel_schedule', name='set_publication_cancel_schedule'),

)
