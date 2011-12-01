from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('api.views',
    url(r'^request/access/$', 'request_access', name='api_request_access'),
    url(r'^request/download/$', 'request_download', name='api_request_download'),


    url(r'^list/publication/$', 'list_publication', name='api_list_publication'),
    url(r'^get/publication/$', 'get_publication', name='api_get_publication'),
    url(r'^search/publication/$', 'search_publication', name='api_search_publication'),

    url(r'^list/shelf/$', 'list_shelf', name='api_list_shelf'),

    
)
