from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('document.views',
    url(r'^org/(?P<organization_slug>\w+)/documents/$', 'view_documents', name='view_documents'),
    url(r'^org/(?P<organization_slug>\w+)/documents/shelf/(?P<shelf_id>\d+)/$', 'view_documents_by_shelf', name='view_documents_by_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/documents/no-shelf/$', 'view_documents_with_no_shelf', name='view_documents_with_no_shelf'),

    url(r'^org/(?P<organization_slug>\w+)/documents/upload/$', 'upload_documents', name='upload_documents'),
    url(r'^org/(?P<organization_slug>\w+)/documents/upload/(?P<shelf_id>\d+)/$', 'upload_documents_to_shelf', name='upload_documents_to_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/documents/upload/finishing/$', 'finishing_upload_documents', name='finishing_upload_documents'),

    url(r'^org/(?P<organization_slug>\w+)/shelf/create/$', 'create_document_shelf', name='create_document_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/shelf/(?P<shelf_id>\d+)/edit/$', 'edit_document_shelf', name='edit_document_shelf'),
    url(r'^org/(?P<organization_slug>\w+)/shelf/(?P<shelf_id>\d+)/delete/$', 'delete_document_shelf', name='delete_document_shelf'),

    # Shelf
    url(r'^document/move/$', 'move_document_to_shelf', name='move_document_to_shelf'),

    # Document

    url(r'^download/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'download_publication', name='download_publication'),
    url(r'^publication/publish/$', 'publish_publication', name='publish_publication'),
    url(r'^publication/unpublish/$', 'unpublish_publication', name='unpublish_publication'),

    url(r'^document/(?P<publication_uid>[a-zA-Z0-9\-]+)/$', 'view_document', name='view_document'),
    url(r'^document/(?P<publication_uid>[a-zA-Z0-9\-]+)/edit/$', 'edit_document', name='edit_document'),
    url(r'^document/(?P<publication_uid>[a-zA-Z0-9\-]+)/delete/$', 'delete_document', name='delete_document'),

)

