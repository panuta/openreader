from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.magazine.views',
    url(r'^publisher/(?P<publisher_id>\d+)/magazines/$', 'view_publisher_magazines', name='view_publisher_magazines'),

    url(r'^publisher/(?P<publisher_id>\d+)/magazines/create/$', 'create_publisher_magazine', name='create_publisher_magazine'),

    url(r'^magazine/(?P<magazine_id>\d+)/$', 'view_magazine', name='view_magazine'),
    url(r'^magazine/issue/(?P<magazine_issue_id>\d+)/$', 'view_magazine_issue', name='view_magazine_issue'),
    url(r'^magazine/(?P<magazine_id>\d+)/edit/$', 'edit_magazine', name='edit_magazine'),
)
