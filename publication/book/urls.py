from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.book.views',
    url(r'^publisher/(?P<publisher_id>\d+)/books/$', 'view_publisher_books', name='view_publisher_books'),

)
