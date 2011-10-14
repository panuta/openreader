import os

from django.conf import settings

from models import UploadingPublication

def upload_publication(uploaded_by, uploading_file, publisher):
    # dir_path = '%s%d/' % (settings.PUBLICATION_ROOT, publisher.id)
    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)

    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    # TODO: determine publication type

    publication = UploadingPublication.objects.create(publisher=publisher, publication_type='ebook', file_name=file_name, file_ext=file_ext, uploaded_by=uploaded_by)
    publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file)

    """
    destination = open('%s%s.%s' % (dir_path, publication.uid, file_ext), 'wb+')
    for chunk in uploading_file.chunks():
        destination.write(chunk)
    destination.close()
    """

    return publication