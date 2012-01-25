import datetime
import logging
import os

from django.conf import settings

from common.thumbnails import get_generator, delete_thumbnails
from common.utilities import split_filename

logger = logging.getLogger(settings.OPENREADER_LOGGER)

from document.models import Publication

def upload_publication(request, publication_type, uploading_file, organization):
    (file_name, file_ext) = split_filename(uploading_file.name)
    publication = Publication.objects.create(organization=organization, title=file_name, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        publication.delete()
        return None

    generator = get_generator(file_ext)
    if generator:
        generated = generator.get_thumbnails(publication.uploaded_file.file)
        publication.has_thumbnail = generated
        publication.save()
    
    publication.is_processing = False
    publication.save()
    
    return publication

def delete_publication(publication):
    delete_thumbnails(publication.uploaded_file)
    publication.uploaded_file.delete()

    PublicationNotice.objects.filter(publication=publication).delete()
    publication.delete()