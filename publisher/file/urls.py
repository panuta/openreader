from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.file.views',
    url(r'^publisher/(?P<publisher_id>\d+)/files/$', 'view_files', name='view_files'),
    url(r'^publisher/files/shelf/(?P<shelf_id>\d+)/$', 'view_files_by_shelf', name='view_files_by_shelf'),
    url(r'^publisher/files/shelf/(?P<shelf_id>\d+)/edit/$', 'edit_file_shelf', name='edit_file_shelf'),

    url(r'^publisher/(?P<publisher_id>\d+)/files/shelf/create/$', 'create_file_shelf', name='create_file_shelf'),
)
