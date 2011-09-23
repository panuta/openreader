import os

from django.conf import settings

from models import UploadingPublication

def upload_publication(uploaded_by, uploading_file, publisher, publication_type, periodical=None):
    dir_path = '%s%d/' % (settings.PUBLICATION_ROOT, publisher.id)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    publication = UploadingPublication(publisher=publisher, periodical=periodical, file_name=file_name, file_ext=file_ext, uploaded_by=uploaded_by)
    if publication_type == 'periodical':
        publication.publication_type = UploadingPublication.UPLOADING_PERIODICAL_ISSUE
    elif publication_type == 'book':
        publication.publication_type = UploadingPublication.UPLOADING_BOOK
    else:
        publication.publication_type = UploadingPublication.UPLOADING_UNDEFINED

    publication.save()

    destination = open('%s%s.%s' % (dir_path, publication.uid, file_ext), 'wb+')
    for chunk in uploading_file.chunks():
        destination.write(chunk)
    destination.close()

    return publication.uid