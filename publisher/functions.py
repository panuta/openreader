import datetime
import logging
import os

from django.conf import settings

from common.thumbnails import get_generator
from common.utilities import splitext

from exceptions import FileUploadTypeUnknown
from models import Publication, PublisherReader, PublicationNotice, PublicationShelf, PublicationReader

logger = logging.getLogger(settings.OPENREADER_LOGGER)

def upload_publication(request, publication_type, uploading_file, publisher):
    (file_name, file_ext) = splitext(uploading_file.name)
    publication = Publication.objects.create(publisher=publisher, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file)
    except:
        publication.delete()
        return None

    generator = get_generator(file_ext)
    if generator:
        processed = generator.get_thumbnails(publication.uploaded_file.file)

        publication.is_processing = not processed
        publication.save()
    
    return publication

def finishing_upload_publication(request, publication, title, description):
    publication.title = title
    publication.description = description
    publication.status = Publication.STATUS['UNPUBLISHED']
    publication.save()

    success_list = request.session.get('finishing_upload_success', [])
    success_list.append(publication)
    request.session['finishing_upload_success'] = success_list

    return publication

def set_publication_unpublished(request, publication):
    publication.web_scheduled = None
    publication.web_scheduled_by = None
    publication.web_published = None
    publication.web_published_by = None
    publication.status = Publication.STATUS['UNPUBLISHED']
    publication.save()

    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_reader.scheduled = None
        pub_reader.scheduled_by = None
        pub_reader.published = None
        pub_reader.published_by = None
        pub_reader.save()
    
    return publication

def set_publication_published(request, publication):
    published = datetime.datetime.today()

    if publication.is_processing:
        PublicationNotice.objects.get_or_create(publication=publication, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY'])
    else:
        publication.status = Publication.STATUS['PUBLISHED']
        publication.web_published = published
    
    publication.web_scheduled = None
    publication.web_scheduled_by = None
    publication.web_published_by = request.user
    publication.save()

    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_reader.scheduled = None
        pub_reader.scheduled_by = None

        if not publication.is_processing:
            pub_reader.published = published
        
        pub_reader.published_by = request.user
        pub_reader.save()
    
    return publication

def set_publication_scheduled(request, publication, schedule):
    publication.web_scheduled = schedule
    publication.web_scheduled_by = request.user
    publication.web_published = None
    publication.web_published_by = None
    publication.status = Publication.STATUS['SCHEDULED']
    publication.save()
    
    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_reader.scheduled = schedule
        pub_reader.scheduled_by = request.user
        pub_reader.published = None
        pub_reader.published_by = None
        pub_reader.save()
    
    return publication

def set_publication_scheduled_cancel(request, publication):
    publication.web_scheduled = None
    publication.web_scheduled_by = None
    publication.web_published = None
    publication.web_published_by = None
    publication.status = Publication.STATUS['UNPUBLISHED']
    publication.save()
    
    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_reader.scheduled = None
        pub_reader.scheduled_by = None
        pub_reader.published = None
        pub_reader.published_by = None
        pub_reader.save()
    
    return publication

def delete_publication(publication):
    from models import publication_media_dir

    try:
        os.remove(publication_media_dir(publication, '%s.%s' % (publication.uid, publication.file_ext)))
    except:
        # TODO: Log error
        pass
    else:
        PublicationNotice.objects.filter(publication=publication).delete()
        PublicationShelf.objects.filter(publication=publication).delete()
        PublicationReader.objects.filter(publication=publication).delete()
        publication.delete()