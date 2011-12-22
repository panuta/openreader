from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('publication.views',

    # Publication
    url(r'^download/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'download_publication', name='download_publication'),

    # Publication Status
    url(r'^publication/publish/$', 'publish_publication', name='publish_publication'),
    url(r'^publication/unpublish/$', 'unpublish_publication', name='unpublish_publication'),
)
