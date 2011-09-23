from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.views',
    url(r'^dashboard/$', 'view_dashboard', name='view_dashboard'),

    url(r'^publisher/create/$', 'create_publisher', name='create_publisher'),
    url(r'^publisher/select/$', 'select_publisher', name='select_publisher'),

    url(r'^get_upload_progress?.*$', 'get_upload_progress', name='get_upload_progress'),

    url(r'^publisher/(?P<publisher_id>\d+)/dashboard/$', 'view_publisher_dashboard', name='view_publisher_dashboard'),

    url(r'^publisher/(?P<publisher_id>\d+)/periodicals/$', 'view_publisher_periodicals', name='view_publisher_periodicals'),

    url(r'^publisher/(?P<publisher_id>\d+)/uploading/periodical/$', 'uploading_periodical_issue', name='uploading_periodical_issue'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/periodical/$', 'upload_periodical_issue', name='upload_periodical_issue'),
    
    url(r'^publisher/(?P<publisher_id>\d+)/books/$', 'view_publisher_books', name='view_publisher_books'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/book/$', 'upload_book', name='upload_book'),

    # Publisher Management
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/profile/$', 'view_publisher_profile', name='view_publisher_profile'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/team/$', 'view_publisher_team', name='view_publisher_team'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/team/invite/$', 'view_publisher_team_invite', name='view_publisher_team_invite'),

    


    url(r'^/periodical/(?P<periodical_id>\d+)/$', 'view_periodical', name='view_periodical'),
    url(r'^/periodical/issue/(?P<periodical_issue_id>\d+)/$', 'view_periodical_issue', name='view_periodical_issue'),

    url(r'^/book/(?P<book_id>\d+)/$', 'view_book', name='view_book'),
)
