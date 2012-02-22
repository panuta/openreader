import datetime, logging, sys, traceback, uuid

from django.conf import settings

from common.thumbnails import generate_thumbnails, delete_thumbnails
from common.utilities import split_filepath

from document.models import Publication

logger = logging.getLogger(settings.OPENREADER_LOGGER)

def upload_publication(request, uploading_file, organization):
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)
    publication = Publication.objects.create(organization=organization, title=file_name, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        publication.delete()
        logger.error(traceback.format_exc(sys.exc_info()[2]))
        return None

    # Create thumbnails
    publication.has_thumbnail = generate_thumbnails(publication)
    publication.save()
    
    return publication

def replace_publication(request, uploading_file, publication):
    if publication.has_thumbnail:
        delete_thumbnails(publication)
    
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)
    new_uid = uuid.uuid4()
    
    try:
        publication.uploaded_file.delete()
        publication.uploaded_file.save('%s.%s' % (new_uid, file_ext), uploading_file.file)
    except:
        logger.error(traceback.format_exc(sys.exc_info()[2]))
        return None
    
    # Change file details
    publication.uid = new_uid
    publication.original_file_name = file_name
    publication.file_ext = file_ext
    publication.replaced = datetime.datetime.now()
    publication.replaced_by = request.user
    
    # Create thumbnails
    publication.has_thumbnail = generate_thumbnails(publication)
    publication.save()

    return publication

def delete_publication(publication):
    if publication.has_thumbnail:
        delete_thumbnails(publication)
    
    publication.uploaded_file.delete()
    publication.delete()

def delete_publications(publications):
    for publication in publications:
        delete_publication(publication)