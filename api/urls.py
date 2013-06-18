from django.conf.urls import patterns, include, url

urlpatterns = patterns('api.views',
    url(r'^list/publication/$', 'list_publication', name='api_list_publication'),
    url(r'^list/organization/$', 'list_user_organization', name='api_list_user_organization'),
    url(r'^config_shelves/$', 'user_config_shelves', name='api_user_config_shelves'),
    url(r'^request/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'request_download_publication', name='api_request_download_publication'),
    url(r'^secret_key/$', 'api_request_secret_key', name='api_request_secret_key'),

    url(r'^subscription/$', 'api_email_subscription', name='api_email_subscription'),

    url(r'^banner/$', 'api_banner', name='api_banner'),
)
