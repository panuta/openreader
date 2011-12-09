from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('document.views',
    url(r'^documents/(?P<organization_id>\d+)/$', 'view_document_front', name='view_document_front'),

)