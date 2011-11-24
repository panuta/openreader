from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.file.views',
    url(r'^publisher/(?P<publisher_id>\d+)/files/$', 'view_files', name='view_files'),

    url(r'^publisher/(?P<publisher_id>\d+)/files/(?P<shelf_id>\d+)/$', 'view_files_by_shelf', name='view_files_by_shelf'),
)
