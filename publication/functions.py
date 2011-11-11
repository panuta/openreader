import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import UploadingPublication

from common.utilities import convert_publication_type

from publication import get_publication_module

def upload_publication(request, module, uploading_file, publisher):
    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    uploading_publication = UploadingPublication.objects.create(publisher=publisher, publication_type=module, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)
    uploading_publication.uploaded_file.save('%s.%s' % (uploading_publication.uid, file_ext), uploading_file)

    return uploading_publication