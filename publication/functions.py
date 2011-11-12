import datetime
import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import UploadingPublication, Publication

from common.modules import get_publication_module

def upload_publication(request, module, uploading_file, publisher):
    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    uploading_publication = UploadingPublication.objects.create(publisher=publisher, publication_type=module, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)
    uploading_publication.uploaded_file.save('%s.%s' % (uploading_publication.uid, file_ext), uploading_file)

    return uploading_publication

def finishing_upload_publication(request, publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time):
    from common.utilities import convert_publish_status
    publish_status = convert_publish_status(publish_status)

    if publish_status == Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH:
        publish_schedule = datetime.datetime(schedule_date.year, schedule_date.month, schedule_date.day, schedule_time.hour, schedule_time.minute)
        published_by = request.user
    else:
        publish_schedule = None
        published_by = None

    if publish_status == Publication.PUBLISH_STATUS_PUBLISHED:
        published = datetime.datetime.today()
        published_by = request.user
    else:
        published = None
    
    publication = Publication.objects.create(
        publisher = publisher,
        uid = uploading_publication.uid,
        title = title,
        description = description,
        publication_type = uploading_publication.publication_type,
        uploaded_file = uploading_publication.uploaded_file,
        original_file_name = uploading_publication.original_file_name,
        file_ext = uploading_publication.file_ext,

        publish_status = publish_status,
        published = published,
        published_by = published_by,

        uploaded = uploading_publication.uploaded,
        uploaded_by = uploading_publication.uploaded_by,
    )

    uploading_publication.delete()
    
    return publication