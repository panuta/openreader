from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.book.views',
    url(r'^publisher/(?P<publisher_id>\d+)/books/$', 'view_book_front', name='view_book_front'),

)
