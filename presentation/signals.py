from django.dispatch.dispatcher import Signal
from common.thumbnails import generate_thumbnails, delete_thumbnails
from domain.models import Publication

# Signal-emitting code... emits whenever a file upload is received
# ----------------------------------------------------------------

publication_uploaded = Signal(providing_args=['data'])


def generate_publication_thumbnail(sender, data, **kwargs):
    print 'Generate publication thumbnail...%s' % data
    try:
        publication = Publication.objects.get(id=data)
        if publication.has_thumbnail:
        	delete_thumbnails(publication)
        publication.has_thumbnail = generate_thumbnails(publication)
        publication.is_processing = False
        publication.save()
    except Publication.DoesNotExist:
        pass

publication_uploaded.connect(generate_publication_thumbnail)
