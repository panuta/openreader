import datetime
import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import UploadingPublication, Publication

def upload_publication(request, publication_type, uploading_file, publisher):
    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    uploading_publication = UploadingPublication.objects.create(publisher=publisher, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)
    uploading_publication.uploaded_file.save('%s.%s' % (uploading_publication.uid, file_ext), uploading_file)

    return uploading_publication

def finishing_upload_publication(request, publisher, uploading_publication, title, description, publish_status, schedule_date, schedule_time):
    
    if publish_status == Publication.PUBLISH_STATUS['UNPUBLISHED']:
        publish_schedule = None
        published = None
        published_by = None

    elif publish_status == Publication.PUBLISH_STATUS['SCHEDULED']:
        publish_schedule = datetime.datetime(schedule_date.year, schedule_date.month, schedule_date.day, schedule_time.hour, schedule_time.minute)
        published = None
        published_by = request.user
    
    elif publish_status == Publication.PUBLISH_STATUS['PUBLISHED']:
        publish_schedule = None
        published = datetime.datetime.today()
        published_by = request.user
    else:
        publish_status = Publication.PUBLISH_STATUS['UNPUBLISHED']
        publish_schedule = None
        published = None
        published_by = None

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
        publish_schedule = publish_schedule,
        published = published,
        published_by = published_by,

        uploaded = uploading_publication.uploaded,
        uploaded_by = uploading_publication.uploaded_by,
    )

    uploading_publication.delete()
    
    return publication

def delete_uploading_publication(uploading_publication):
    from models import publication_media_dir

    try:
        os.remove(publication_media_dir(uploading_publication, '%s.%s' % (uploading_publication.uid, uploading_publication.file_ext)))
    except:
        # TODO: Log error
        pass
    
    uploading_publication.delete()