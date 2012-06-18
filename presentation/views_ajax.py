# -*- encoding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.utils import simplejson

from common.shortcuts import response_json_success, response_json_error
from common.utilities import format_abbr_datetime, humanize_file_size

from accounts.permissions import get_backend as get_permission_backend

from domain import functions as domain_functions
from domain.models import OrganizationTag, PublicationTag, Publication, Organization, UserGroup, UserOrganizationInvitation, OrganizationGroup, UserOrganization, OrganizationShelf
from domain.tasks import generate_thumbnails

logger = logging.getLogger(settings.OPENREADER_LOGGER)

@require_POST
@login_required
def ajax_resend_user_invitation(request, invitation_id):
    if request.is_ajax():
        invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
        organization = invitation.organization

        if not get_permission_backend(request).can_manage_user(request.user, organization):
            raise Http404

        if invitation.send_invitation_email():
            return response_json_success()
        else:
            return response_json_error('send-invitation-failed')
    else:
        raise Http404


@require_POST
@login_required
def ajax_cancel_user_invitation(request, invitation_id):
    if request.is_ajax():
        invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
        organization = invitation.organization

        if not get_permission_backend(request).can_manage_user(request.user, organization):
            raise Http404

        invitation.delete()

        return response_json_success({'redirect_url':reverse('view_organization_invited_users', args=[organization.slug])})
    else:
        raise Http404


@require_POST
@login_required
def ajax_remove_organization_user(request, organization_user_id):
    if request.is_ajax():
        user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
        organization = user_organization.organization

        if not get_permission_backend(request).can_manage_user(request.user, organization):
            raise Http404

        user_organization.is_active = False
        user_organization.save()

        messages.success(request, u'ถอดผู้ใช้ออกจากบริษัทเรียบร้อย')
        return response_json_success({'redirect_url':reverse('view_organization_users', args=[organization.slug])})
    else:
        raise Http404


@require_POST
@login_required
def ajax_remove_organization_group(request, organization_group_id):
    if request.is_ajax():
        group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
        organization = group.organization

        if not get_permission_backend(request).can_manage_group(request.user, organization):
            raise Http404

        UserGroup.objects.filter(group=group).delete()
        group.delete()

        messages.success(request, u'ลบกลุ่มผู้ใช้เรียบร้อย')
        return response_json_success({'redirect_url':reverse('view_organization_groups', args=[organization.slug])})
    else:
        raise Http404


@require_GET
@login_required
def ajax_query_users(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_view_organization(request.user, organization):
        raise Http404

    query_string = request.GET.get('q')

    if query_string:
        result = []

        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
        model = models.get_model(app_label, model_name)
        for user_profile in model._default_manager.filter(user__userorganization__organization=organization).filter(Q(first_name__icontains=query_string) | Q(last_name__icontains=query_string)):
            result.append({'name':user_profile.get_fullname(), 'value':str(user_profile.user.id)})

        return HttpResponse(simplejson.dumps(result))

    raise Http404


@require_GET
@login_required
def ajax_query_groups(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not get_permission_backend(request).can_view_organization(request.user, organization):
        raise Http404

    result = []
    organization_groups = OrganizationGroup.objects.filter(organization=organization).order_by('name')
    for organization_group in organization_groups:
        result.append([organization_group.id, organization_group.name])

    return HttpResponse(simplejson.dumps(result))


# Publication
########################################################################################################################

def ajax_query_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not get_permission_backend(request).can_view_publication(request.user, publication.organization, {'publication':publication}):
        raise Http404

    return response_json_success({
        'uid': str(publication.uid),
        'title': publication.title,
        'description': publication.description,
        'tag_names': ','.join([tag.tag_name for tag in publication.tags.all()]),
        'uploaded': format_abbr_datetime(publication.uploaded),
        'file_ext': publication.file_ext,
        'file_size_text': humanize_file_size(publication.uploaded_file.file.size),

        'thumbnail_url':publication.get_large_thumbnail(),
        'download_url': reverse('download_publication', args=[publication.uid]),
    })


@transaction.commit_manually
@require_POST
@login_required
def upload_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    shelf_id = request.POST.get('shelf')
    if shelf_id:
        shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)
    else:
        transaction.rollback()
        raise Http404

    if shelf.organization.id != organization.id or not get_permission_backend(request).can_upload_shelf(request.user, organization, {'shelf':shelf}):
        transaction.rollback()
        raise Http404

    try:
        file = request.FILES[u'files[]']

        if file.size > settings.MAX_PUBLICATION_FILE_SIZE:
            transaction.rollback()
            return response_json_error('file-size-exceed')

        uploading_file = UploadedFile(file)
        publication = domain_functions.upload_publication(request, uploading_file, organization, shelf)

        if not publication:
            transaction.rollback()
            return response_json_error()

        transaction.commit() # Need to commit before create task

        try:
            generate_thumbnails.delay(publication.uid)
        except:
            import sys
            import traceback
            logger.critical(traceback.format_exc(sys.exc_info()[2]))

        return response_json_success({
            'uid': str(publication.uid),
            'title': publication.title,
            'file_ext':publication.file_ext,
            'file_size_text': humanize_file_size(uploading_file.file.size),
            'shelf':shelf.id if shelf else '',
            'uploaded':format_abbr_datetime(publication.uploaded),
            'thumbnail_url':publication.get_large_thumbnail(),
            'download_url': reverse('download_publication', args=[publication.uid])
        })

    except:
        transaction.rollback()
        return response_json_error()


@transaction.commit_manually
@require_POST
@login_required
def replace_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    publication_id = request.POST.get('publication_id')
    print publication_id
    if publication_id:
        publication = get_object_or_404(Publication, uid=publication_id)
    else:
        transaction.rollback()
        raise Http404

    if not get_permission_backend(request).can_edit_publication(request.user, publication.organization, {'publication':publication}):
        transaction.rollback()
        raise Http404

    try:
        file = request.FILES[u'files[]']

        if file.size > settings.MAX_PUBLICATION_FILE_SIZE:
            transaction.rollback()
            return response_json_error('file-size-exceed')

        uploading_file = UploadedFile(file)
        publication = domain_functions.replace_publication(request, uploading_file, publication)

        if not publication:
            transaction.rollback()
            return response_json_error()

        transaction.commit()

        try:
            generate_thumbnails.delay(publication.uid)
        except:
            import sys
            import traceback
            logger.critical(traceback.format_exc(sys.exc_info()[2]))

        return response_json_success({
            'uid': str(publication.uid),
            'file_ext':publication.file_ext,
            'file_size_text': humanize_file_size(uploading_file.file.size),
            'uploaded':format_abbr_datetime(publication.uploaded),
            'replaced':format_abbr_datetime(publication.replaced),
            'thumbnail_url':publication.get_large_thumbnail(),
            'download_url': reverse('download_publication', args=[publication.uid])
        })

    except:
        transaction.rollback()
        return response_json_error()


@require_POST
@login_required
def ajax_edit_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    publication_uid = request.POST.get('uid')
    title = request.POST.get('title')
    description = request.POST.get('description')
    tag_names = request.POST.get('tags')

    try:
        publication = Publication.objects.get(uid=publication_uid)
    except Publication.DoesNotExist:
        return response_json_error('invalid-publication')

    if not get_permission_backend(request).can_edit_publication(request.user, organization, {'publication':publication}):
        raise Http404

    if not title:
        return response_json_error('missing-parameter')

    publication.title = title
    publication.description = description
    publication.save()

    PublicationTag.objects.filter(publication=publication).delete()

    tag_names = tag_names.split(',')
    for tag_name in tag_names:
        if tag_name:
            tag_name = tag_name.lower().strip()
            try:
                tag = OrganizationTag.objects.get(organization=organization, tag_name=tag_name)
            except OrganizationTag.DoesNotExist:
                tag = OrganizationTag.objects.create(organization=organization, tag_name=tag_name)

            PublicationTag.objects.get_or_create(publication=publication, tag=tag)

    return response_json_success()


@require_POST
@login_required
def ajax_delete_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    publication_uid = request.POST.get('uid')

    if publication_uid:
        publication_uids = [publication_uid]
    else:
        publication_uids = request.POST.getlist('uid[]')

        if not publication_uids:
            raise Http404

    publications = []
    for publication_uid in publication_uids:
        try:
            publication = Publication.objects.get(uid=publication_uid)
        except Publication.DoesNotExist:
            continue

        if get_permission_backend(request).can_edit_publication(request.user, organization, {'publication':publication}):
            publications.append(publication)

    if not publications:
        return response_json_error('invalid-publication')

    domain_functions.delete_publications(publications)

    return response_json_success()


@require_POST
@login_required
def ajax_add_publications_tag(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    publication_uids = request.POST.getlist('publication[]')
    tag_names = request.POST.get('tags')

    if tag_names:
        publications = []
        for publication_uid in publication_uids:
            try:
                publication = Publication.objects.get(uid=publication_uid)
            except Publication.DoesNotExist:
                continue

            if get_permission_backend(request).can_edit_publication(request.user, organization, {'publication':publication}):
                publications.append(publication)

        tag_names = tag_names.split(',')
        saved_tag_names = []
        if publications and tag_names:
            for tag_name in tag_names:
                if tag_name:
                    tag_name = tag_name.lower().strip()

                    try:
                        tag = OrganizationTag.objects.get(organization=organization, tag_name=tag_name)
                    except OrganizationTag.DoesNotExist:
                        tag = OrganizationTag.objects.create(organization=organization, tag_name=tag_name)

                    for publication in publications:
                        publication_tag, created = PublicationTag.objects.get_or_create(publication=publication, tag=tag)

                        if created:
                            saved_tag_names.append(tag_name)

            return response_json_success({'tag_names':saved_tag_names})

        else:
            return response_json_error('invalid-publication')

    else:
        return response_json_error('missing-parameter')


@require_GET
@login_required
def ajax_query_publication_tags(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    term = request.GET.get('term')

    if not get_permission_backend(request).can_view_organization(request.user, organization):
        raise Http404

    tags = OrganizationTag.objects.filter(organization=organization, tag_name__icontains=term)

    result = []
    for tag in tags:
        result.append({'id':str(tag.id), 'label':tag.tag_name, 'value':tag.tag_name})

    return HttpResponse(simplejson.dumps(result))