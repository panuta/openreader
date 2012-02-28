from celery.task import task

@task(name='tasks.prepare_publication')
def prepare_publication(publication_uid):

    from common.thumbnails import generate_thumbnails, delete_thumbnails
    from document.models import Publication

    publication = Publication.objects.get(uid=publication_uid)

    if publication.has_thumbnail:
        delete_thumbnails(publication)

    publication.has_thumbnail = generate_thumbnails(publication)
    
    # TODO Upload to file servers

    publication.is_processing = False
    publication.save()

    return publication_uid