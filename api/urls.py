from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('api.views',
    url(r'^request/access/$', 'request_access', name='api_request_access'),
    url(r'^request/download/$', 'request_download', name='api_request_download'),
    
    url(r'^get/publication/new_release/$', 'get_publication_new_release', name='api_get_publication_new_release'),
    url(r'^get/publication/top_charts/$', 'get_publication_top_charts', name='api_get_publication_top_charts'),
    url(r'^get/publication/categories/$', 'get_publication_categories', name='api_get_publication_categories'),
    url(r'^get/publication/list/$', 'get_publication_list', name='api_get_publication_list'),
    url(r'^get/publication/covers/$', 'get_publication_covers', name='api_get_publication_covers'),
    url(r'^get/publication/details/$', 'get_publication_details', name='api_get_publication_details'),

    url(r'^search/publication/$', 'search_publication', name='api_search_publication'),

    url(r'^get/accounts/purchase_history/$', 'get_accounts_purchase_history', name='api_get_accounts_purchase_history'),
)
