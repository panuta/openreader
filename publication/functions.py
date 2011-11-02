import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import UploadingPublication

def upload_publication(uploaded_by, uploading_file, publisher, publication_type=None, parent_id=None):
    # dir_path = '%s%d/' % (settings.PUBLICATION_ROOT, publisher.id)
    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)

    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    if publication_type in ('periodical', 'book'):
        if file_ext not in ('pdf'):
            raise FileUploadTypeUnknown()

    elif publication_type == 'video':
        if file_ext not in ('mov', 'avi', 'mp4'):
            raise FileUploadTypeUnknown()

    elif not publication_type:
        # Check publication type from file extension
        if file_ext in ('mov', 'avi', 'mp4'):
            publication_type = 'video'
        else:
            raise FileUploadTypeUnknown()
    
    publication = UploadingPublication.objects.create(publisher=publisher, publication_type=publication_type, parent_id=parent_id, original_file_name=file_name, file_ext=file_ext, uploaded_by=uploaded_by)
    publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file)

    """
    destination = open('%s%s.%s' % (dir_path, publication.uid, file_ext), 'wb+')
    for chunk in uploading_file.chunks():
        destination.write(chunk)
    destination.close()
    """

    return publication