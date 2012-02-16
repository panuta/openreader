import logging
import datetime
import uuid

from django.conf import settings

from common.thumbnails import get_generator, delete_thumbnails
from common.utilities import split_filepath

logger = logging.getLogger(settings.OPENREADER_LOGGER)

from document.models import Publication

def upload_publication(request, uploading_file, organization):
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)
    publication = Publication.objects.create(organization=organization, title=file_name, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        publication.delete()
        return None

    # Create thumbnails
    generator = get_generator(file_ext)
    if generator:
        generated = generator.generate_thumbnails(publication.uploaded_file.file)
        publication.has_thumbnail = generated
    else:
        publication.has_thumbnail = False
    
    publication.save()
    
    return publication

def replace_publication(request, uploading_file, publication):
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)
    
    try:
        publication.uploaded_file.delete()
        publication.uploaded_file.save('%s.%s' % (uuid.uuid4(), file_ext), uploading_file.file)
    except:
        return None
    
    # Create thumbnails
    if publication.has_thumbnail:
        delete_thumbnails(publication.uploaded_file)
    generator = get_generator(file_ext)
    if generator:
        generated = generator.generate_thumbnails(publication.uploaded_file.file)
        publication.has_thumbnail = generated
    else:
        publication.has_thumbnail = False
    
    # Change file details
    publication.original_file_name = file_name
    publication.file_ext = file_ext
    publication.replaced = datetime.datetime.now()
    publication.replaced_by = request.user
    publication.save()

    return publication

def download_publication(publication):
    pass

def delete_publication(publication):
    if publication.has_thumbnail:
        delete_thumbnails(publication.uploaded_file)
    publication.uploaded_file.delete()
    publication.delete()

def delete_publications(publications):
    for publication in publications:
        delete_publication(publication)