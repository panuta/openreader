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
        logger.crirical(traceback.format_exc(sys.exc_info()[2]))
        return None

    try:
        if publication.has_thumbnail:
            delete_thumbnails(publication)

        publication.has_thumbnail = generate_thumbnails(publication)
    except:
        publication.has_thumbnail = False
        logger.error(traceback.format_exc(sys.exc_info()[2]))
    
    # TODO Upload to file servers

    publication.is_processing = False
    publication.save()

    return publication_uid