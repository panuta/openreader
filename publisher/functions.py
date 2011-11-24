import datetime
import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import Publication

def upload_publication(request, publication_type, uploading_file, publisher):
    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    publication = Publication.objects.create(publisher=publisher, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)
    publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file)

    # Generate file thumbnails

    return publication

def finishing_upload_publication(request, publication, title, description, publish_status, schedule_date, schedule_time):
    
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
        publish_status = Publication.PUBLISH_STATUS['UPLOADING']
        publish_schedule = None
        published = None
        published_by = None
    
    publication.title = title
    publication.description = description
    publication.publish_status = publish_status
    publication.publish_schedule = publish_schedule
    publication.published = published
    publication.published_by = published_by
    publication.save()
    
    return publication

def delete_publication(publication):
    from models import publication_media_dir

    try:
        os.remove(publication_media_dir(publication, '%s.%s' % (publication.uid, publication.file_ext)))
    except:
        # TODO: Log error
        pass
    else:
        PublicationShelf.objects.filter(publication=publication).delete()
        publication.delete()