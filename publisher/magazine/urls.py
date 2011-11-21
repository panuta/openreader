from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.magazine.views',
    url(r'^publisher/(?P<publisher_id>\d+)/magazines/$', 'view_magazines', name='view_magazines'),

    url(r'^publisher/(?P<publisher_id>\d+)/magazines/create/$', 'create_magazine', name='create_magazine'),

    url(r'^magazine/(?P<magazine_id>\d+)/$', 'view_magazine', name='view_magazine'),
    url(r'^magazine/(?P<magazine_id>\d+)/edit/$', 'edit_magazine', name='edit_magazine'),
    url(r'^magazine/(?P<magazine_id>\d+)/delete/$', 'delete_magazine', name='delete_magazine'),
    
)
