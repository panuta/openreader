from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('management.views',
    url(r'^$', 'manage_front', name='manage_front'),
    url(r'^publishers/$', 'manage_publishers', name='manage_publishers'),
    url(r'^publishers/create/$', 'create_publisher', name='manage.create_publisher'),

    url(r'^publisher/(?P<publisher_id>\d+)/$', 'manage_publisher', name='manage_publisher'),


    

    
    
    
)
