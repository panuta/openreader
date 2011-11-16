from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publisher.book.views',
    url(r'^publisher/(?P<publisher_id>\d+)/books/$', 'view_books', name='view_books'),

)
