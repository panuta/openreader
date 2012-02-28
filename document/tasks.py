import logging
import sys

from celery.task import task

from django.conf import settings

logger = logging.getLogger(settings.OPENREADER_LOGGER)

@task(name='tasks.prepare_publication')
def prepare_publication(publication_uid):

    from common.thumbnails import generate_thumbnails, delete_thumbnails
    from document.models import Publication

    try:
        publication = Publication.objects.get(uid=publication_uid)
    except:
        logger.critical(traceback.format_exc(sys.exc_info()[2]))
        return None

    # Generate thumbnails
    try:
        if publication.has_thumbnail:
            delete_thumbnails(publication)

        publication.has_thumbnail = generate_thumbnails(publication)
    except:
        publication.has_thumbnail = False
        logger.error(traceback.format_exc(sys.exc_info()[2]))
    
    # Upload publication
    from common.fileservers import upload_to_server

    for server in OrganizationDownloadServer.objects.filter(organization=publication.organization).order_by('-priority'):
        upload_to_server(server, publication)

    publication.is_processing = False
    publication.save()

    return publication_uid

