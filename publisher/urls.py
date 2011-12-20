from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.views',

    # view_publisher_front

    # Dashboard
    url(r'^dashboard/$', 'view_dashboard', name='view_dashboard'),
    url(r'^publisher/(?P<publisher_id>\d+)/dashboard/$', 'view_publisher_dashboard', name='view_publisher_dashboard'),

    # Upload
    url(r'^publisher/(?P<publisher_id>\d+)/upload/(?P<module_name>\w+)/$', 'upload_publication', name='upload_module_publication'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/$', 'upload_publication', name='upload_publication'),
    url(r'^publication/(?P<publication_id>\d+)/finishing_upload/$', 'finishing_upload_publication', name='finishing_upload_publication'),
    url(r'^publication/(?P<publication_id>\d+)/upload/cancel/$', 'cancel_upload_publication', name='cancel_upload_publication'),
    
    url(r'^get_upload_progress?.*$', 'get_upload_progress', name='get_upload_progress'),

    # Publication
    url(r'^publication/(?P<publication_id>\d+)/$', 'view_publication', name='view_publication'),
    url(r'^publication/(?P<publication_id>\d+)/download/$', 'download_publication', name='download_publication'),
    url(r'^get/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'get_publication', name='get_publication'),

    url(r'^publication/(?P<publication_id>\d+)/edit/$', 'edit_publication', name='edit_publication'),
    url(r'^publication/(?P<publication_id>\d+)/edit/status/$', 'edit_publication_status', name='edit_publication_status'),
    url(r'^publication/(?P<publication_id>\d+)/replace/$', 'replace_publication', name='replace_publication'),
    url(r'^publication/(?P<publication_id>\d+)/delete/$', 'delete_publication', name='delete_publication'),

    url(r'^publication/(?P<publication_id>\d+)/set/published/$', 'set_publication_published', name='set_publication_published'),
    url(r'^publication/(?P<publication_id>\d+)/set/schedule/$', 'set_publication_schedule', name='set_publication_schedule'),
    url(r'^publication/(?P<publication_id>\d+)/set/cancel_schedule/$', 'set_publication_cancel_schedule', name='set_publication_cancel_schedule'),

)
