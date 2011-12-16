import datetime
import logging
import os

from django.conf import settings

from common.thumbnails import get_generator
from common.utilities import splitext

logger = logging.getLogger(settings.OPENREADER_LOGGER)

from publication.models import Publication, PublicationNotice

def upload_publication(request, publication_type, uploading_file, organization):
    (file_name, file_ext) = splitext(uploading_file.name)
    publication = Publication.objects.create(organization=organization, title=file_name, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        publication.delete()
        return None

    generator = get_generator(file_ext)
    if generator:
        processed = generator.get_thumbnails(publication.uploaded_file.file)

        publication.is_processing = not processed
        publication.save()
    
    return publication

def publish_publication(request, publication):
    published = datetime.datetime.today()

    if publication.is_processing:
        PublicationNotice.objects.get_or_create(publication=publication, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY'])
    else:
        publication.status = Publication.STATUS['PUBLISHED']
        publication.published = published
    
    publication.scheduled = None
    publication.scheduled_by = None
    publication.published_by = request.user
    publication.save()
    
    return publication