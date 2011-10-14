from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.views',
    url(r'^dashboard/$', 'view_dashboard', name='view_dashboard'),

    url(r'^publisher/create/$', 'create_publisher', name='create_publisher'),
    url(r'^publisher/select/$', 'select_publisher', name='select_publisher'),

    # Upload
    url(r'^get_upload_progress?.*$', 'get_upload_progress', name='get_upload_progress'),
    url(r'^publisher/(?P<publisher_id>\d+)/upload/$', 'upload_publication', name='upload_publication'),
    url(r'^publication/(?P<publication_id>\d+)/finish_upload/$', 'finish_upload_publication', name='finish_upload_publication'),





    url(r'^publisher/(?P<publisher_id>\d+)/dashboard/$', 'view_publisher_dashboard', name='view_publisher_dashboard'),

    url(r'^publisher/(?P<publisher_id>\d+)/periodicals/$', 'view_publisher_periodicals', name='view_publisher_periodicals'),

    url(r'^publisher/(?P<publisher_id>\d+)/books/$', 'view_publisher_books', name='view_publisher_books'),
    
    # Publisher Management
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/profile/$', 'view_publisher_profile', name='view_publisher_profile'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/team/$', 'view_publisher_team', name='view_publisher_team'),
    url(r'^publisher/(?P<publisher_id>\d+)/publisher/team/invite/$', 'view_publisher_team_invite', name='view_publisher_team_invite'),

    # Publication
    url(r'^publication/(?P<publication_id>\d+)/$', 'view_publication', name='view_publication'),
    url(r'^publication/(?P<publication_id>\d+)/download/$', 'download_publication', name='download_publication'),
    url(r'^get/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'get_publication', name='get_publication'),

    url(r'^periodical/(?P<periodical_id>\d+)/$', 'view_periodical', name='view_periodical'),
    url(r'^periodical/issue/(?P<periodical_issue_id>\d+)/$', 'view_periodical_issue', name='view_periodical_issue'),

    url(r'^book/(?P<book_id>\d+)/$', 'view_book', name='view_book'),
)
