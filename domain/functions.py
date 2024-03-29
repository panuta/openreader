import logging, sys, traceback, uuid

from django.conf import settings

from common.thumbnails import delete_thumbnails
from common.utilities import split_filepath
from django.utils.timezone import now

from domain.models import Publication, PublicationShelf, OrganizationShelf, OrganizationShelfPermission, GroupShelfPermission, UserShelfPermission, UserOrganizationInvitation, OrganizationGroup, UserOrganization

logger = logging.getLogger(settings.OPENREADER_LOGGER)

def upload_publication(request, uploading_file, organization, shelf):
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)
    publication = Publication.objects.create(organization=organization, title=file_name, original_file_name=file_name, file_ext=file_ext, uploaded_by=request.user)

    try:
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        publication.delete()
        logger.critical(traceback.format_exc(sys.exc_info()[2]))
        return None

    PublicationShelf.objects.create(publication=publication, shelf=shelf, created_by=request.user)

    return publication


def replace_publication(request, uploading_file, publication):
    (file_path, file_name, file_ext) = split_filepath(uploading_file.name)

    try:
        publication.uploaded_file.delete()
        publication.uploaded_file.save('%s.%s' % (publication.uid, file_ext), uploading_file.file)
    except:
        logger.critical(traceback.format_exc(sys.exc_info()[2]))
        return None

    # Change file details
    publication.original_file_name = file_name
    publication.file_ext = file_ext
    publication.replaced = now()
    publication.replaced_by = request.user
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


def _remove_all_shelves(organization):
    shelves = OrganizationShelf.objects.filter(organization=organization)

    for shelf in shelves:
        for publication in Publication.objects.filter(shelves__in=[shelf]):
            delete_publication(publication)

        PublicationShelf.objects.filter(shelf=shelf).delete()
        OrganizationShelfPermission.objects.filter(shelf=shelf).delete()
        GroupShelfPermission.objects.filter(shelf=shelf).delete()
        UserShelfPermission.objects.filter(shelf=shelf).delete()
        shelf.delete()


def remove_organization(organization):
    _remove_all_shelves(organization)

    UserOrganizationInvitation.objects.filter(organization=organization).delete()
    OrganizationGroup.objects.filter(organization=organization).delete()
    UserOrganization.objects.filter(organization=organization).delete()
    organization.delete()