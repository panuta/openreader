from django.conf.urls import patterns, include, url

urlpatterns = patterns('api.views',
    url(r'^request/access/$', 'request_access', name='api_request_access'),
    url(r'^list/publication/$', 'list_publication', name='api_list_publication'),
    url(r'^get/user_organization/$', 'get_user_organization', name='api_get_user_organization'),
    
    url(r'^request/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'request_download_publication', name='api_request_download_publication'),
)
