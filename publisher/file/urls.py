from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.file.views',
    url(r'^publisher/(?P<publisher_id>\d+)/files/$', 'view_files', name='view_files'),

)
