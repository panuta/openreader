# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.utils import simplejson

from common.shortcuts import response_json_success, response_json_error

from accounts.permissions import get_backend as get_permission_backend

from domain import functions as domain_functions
from domain.models import OrganizationTag, PublicationTag, Publication, Organization, UserGroup

@require_POST
@login_required
def ajax_resend_user_invitation(request, invitation_id):

    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    invitation.send_invitation_email()

    messages.success(request, u'ส่งคำขอถึงผู้ใช้เรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_invited_users', args=[organization.slug])})

@require_POST
@login_required
def ajax_cancel_user_invitation(request, invitation_id):
    invitation = get_object_or_404(UserOrganizationInvitation, pk=invitation_id)
    organization = invitation.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    invitation.delete()

    messages.success(request, u'เพิกถอนคำขอเรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_invited_users', args=[organization.slug])})

@require_POST
@login_required
def ajax_remove_organization_user(request, organization_user_id):

    user_organization = get_object_or_404(UserOrganization, pk=organization_user_id)
    organization = user_organization.organization

    if not get_permission_backend(request).can_manage_user(request.user, organization):
        raise Http404

    user_organization.is_active = False
    user_organization.save()

    messages.success(request, u'ถอดผู้ใช้ออกจากบริษัทเรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_users', args=[organization.slug])})

@require_POST
@login_required
def ajax_remove_organization_group(request, organization_group_id):
    group = get_object_or_404(OrganizationGroup, pk=organization_group_id)
    organization = group.organization

    if not get_permission_backend(request).can_manage_group(request.user, organization):
        raise Http404

    UserGroup.objects.filter(group=group).delete()
    group.delete()

    messages.success(request, u'ลบกลุ่มผู้ใช้เรียบร้อย')
    return response_json_success({'redirect_url':reverse('view_organization_groups', args=[organization.slug])})

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



@require_POST
@login_required
def ajax_edit_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    publication_uid = request.POST.get('uid')
    title = request.POST.get('title')
    description = request.POST.get('description')
    tag_names = request.POST.getlist('tags[]')

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

    for tag_name in tag_names:
        if tag_name:
            try:
                tag = OrganizationTag.objects.get(organization=organization, tag_name=tag_name)
            except OrganizationTag.DoesNotExist:
                tag = OrganizationTag.objects.create(organization=organization, tag_name=tag_name)

            PublicationTag.objects.create(publication=publication, tag=tag)

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
    tag_name = request.POST.get('tag')

    if tag_name:
        publications = []
        for publication_uid in publication_uids:
            try:
                publication = Publication.objects.get(uid=publication_uid)
            except Publication.DoesNotExist:
                continue

            if get_permission_backend(request).can_edit_publication(request.user, organization, {'publication':publication}):
                publications.append(publication)

        if publications:
            try:
                tag = OrganizationTag.objects.get(organization=organization, tag_name=tag_name)
            except OrganizationTag.DoesNotExist:
                tag = OrganizationTag.objects.create(organization=organization, tag_name=tag_name)

            for publication in publications:
                PublicationTag.objects.get_or_create(publication=publication, tag=tag)

            return response_json_success()

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