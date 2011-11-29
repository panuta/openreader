import datetime
import os

from django.conf import settings

from exceptions import FileUploadTypeUnknown
from models import Publication, PublisherReader

def upload_publication(request, publication_type, uploading_file, publisher):
    (file_name, separator, file_ext) = uploading_file.name.rpartition('.')

    publication = Publication.objects.create(publisher=publisher, publication_type=publication_type, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)
    publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file)

    # Generate file thumbnails

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

def publish_publication(request, publication):
    published = datetime.datetime.today()

    publication.status = Publication.STATUS['PUBLISHED']
    publication.web_scheduled = None
    publication.web_scheduled_by = None
    publication.web_published = published
    publication.web_published_by = request.user
    publication.save()

    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_readers.append(pub_reader)

        pub_reader.scheduled = None
        pub_reader.scheduled_by = None
        pub_reader.published = published
        pub_reader.published_by = request.user
        pub_reader.save()
    
    # TODO: put publication on queue if the status is PROGRESSING
    
    return publication

def schedule_publication(request, publication, schedule):
    publication.status = Publication.STATUS['SCHEDULED']
    publication.web_scheduled = schedule
    publication.web_scheduled_by = request.user
    publication.web_published = None
    publication.web_published_by = None
    publication.save()
    
    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_readers.append(pub_reader)

        pub_reader.scheduled = schedule
        pub_reader.scheduled_by = request.user
        pub_reader.published = None
        pub_reader.published_by = None
        pub_reader.save()
    
    # TODO: put publication on queue if the status is PROGRESSING
    
    return publication

def cancel_schedule_publication(request, publication):
    publication.web_scheduled = None
    publication.web_scheduled_by = None
    publication.web_published = None
    publication.web_published_by = None
    publication.save()
    
    for reader in PublisherReader.objects.filter(publisher=publication.publisher):
        pub_reader, created = PublicationReader.objects.get_or_create(publication=publication, reader=reader)
        pub_readers.append(pub_reader)

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
        PublicationShelf.objects.filter(publication=publication).delete()
        PublicationReader.objects.filter(publication=publication).delete()
        publication.delete()