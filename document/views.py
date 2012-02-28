# -*- encoding: utf-8 -*-
import datetime
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from django.utils import simplejson

from private_files.views import get_file as private_files_get_file
from httpauth import logged_in_or_basicauth

from common.permissions import can
from common.shortcuts import response_json, response_json_success, response_json_error
from common.utilities import format_abbr_datetime, humanize_file_size

from accounts.models import Organization, UserOrganization, OrganizationGroup
from document import functions as document_functions

from forms import *
from models import *
from permissions import *
from tasks import prepare_publication

logger = logging.getLogger(settings.OPENREADER_LOGGER)

@login_required
def view_organization_front(request, organization_slug):
    return redirect('view_documents', organization_slug=organization_slug)

@require_GET
@login_required
def view_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view_organization', organization):
        raise Http404

    shelves = get_viewable_shelves(request.user, organization)
    publications = Publication.objects.filter(shelves__in=shelves).order_by('-uploaded')
    return render(request, 'document/documents.html', {'organization':organization, 'publications':publications, 'shelf':None, 'shelf_type':'all'})

@require_GET
@login_required
def view_documents_by_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'view_shelf', organization, {'shelf':shelf}):
        raise Http404

    publications = Publication.objects.filter(organization=organization, shelves__in=[shelf]).order_by('-uploaded')
    return render(request, 'document/documents.html', {'organization':organization, 'publications':publications, 'shelf':shelf, 'shelf_type':'shelf'})

# PUBLICATION
######################################################################################################################################################

@transaction.commit_manually
@require_POST
@login_required
def upload_publication(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'upload_shelf', organization, {'shelf':shelf}):
        raise Http404

    try:
        file = request.FILES[u'files[]']

        if file.size > settings.MAX_PUBLICATION_FILE_SIZE:
            return response_json_error('file-size-exceed')

        uploading_file = UploadedFile(file)
        publication = document_functions.upload_publication(request, uploading_file, organization, shelf)

        if not publication:
            transaction.rollback()
            return response_json_error()

        transaction.commit() # Need to commit before create task

        try:
            prepare_publication.delay(publication.uid)
        except:
            logger.crirical(traceback.format_exc(sys.exc_info()[2]))

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

@require_GET
@login_required
def download_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not can(request.user, 'view_publication', publication.organization, {'publication':publication}):
        raise Http404
    
    return private_files_get_file(request, 'document', 'Publication', 'uploaded_file', str(publication.id), '%s.%s' % (publication.original_file_name, publication.file_ext))

@transaction.commit_manually
@require_POST
@login_required
def replace_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if not can(request.user, 'edit_publication', publication.organization, {'publication':publication}):
        raise Http404

    try:
        file = request.FILES[u'files[]']

        if file.size > settings.MAX_PUBLICATION_FILE_SIZE:
            return response_json_error('file-size-exceed')

        uploading_file = UploadedFile(file)
        publication = document_functions.replace_publication(request, uploading_file, publication)

        if not publication:
            transaction.rollback()
            return response_json_error()

        transaction.commit()
        prepare_publication.delay(publication.uid)

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
    tag_names = request.POST.getlist('tags[]')

    try:
        publication = Publication.objects.get(uid=publication_uid)
    except Publication.DoesNotExist:
        return response_json_error('invalid-publication')
    
    if not can(request.user, 'edit_publication', organization, {'publication':publication}):
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
        
        if can(request.user, 'edit_publication', organization, {'publication':publication}):
            publications.append(publication)
    
    if not publications:
        return response_json_error('invalid-publication')
    
    document_functions.delete_publications(publications)

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
            
            if can(request.user, 'edit_publication', organization, {'publication':publication}):
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

    if not can(request.user, 'view_organization', organization):
        raise Http404

    tags = OrganizationTag.objects.filter(organization=organization, tag_name__icontains=term)

    result = []
    for tag in tags:
        result.append({'id':str(tag.id), 'label':tag.tag_name, 'value':tag.tag_name})
    
    return HttpResponse(simplejson.dumps(result))

# SHELF
######################################################################################################################################################

def _persist_shelf_permissions(request, organization, shelf):
    OrganizationShelfPermission.objects.filter(shelf=shelf).delete()
    GroupShelfPermission.objects.filter(shelf=shelf).delete()
    UserShelfPermission.objects.filter(shelf=shelf).delete()

    for permission in request.POST.getlist('permission'):
        permit = permission.split('-')

        if permit[0] == 'all':
            OrganizationShelfPermission.objects.create(shelf=shelf, access_level=int(permit[1]), created_by=request.user)
            
        elif permit[0] == 'group':
            group = get_object_or_404(OrganizationGroup, pk=int(permit[1]))
            GroupShelfPermission.objects.create(shelf=shelf, group=group, access_level=int(permit[2]), created_by=request.user)
            
        elif permit[0] == 'user':
            user = get_object_or_404(User, pk=int(permit[1]))
            UserShelfPermission.objects.create(shelf=shelf, user=user, access_level=int(permit[2]), created_by=request.user)

def _extract_shelf_permissions(shelf):
    shelf_permissions = []

    try:
        organization_shelf_permission = OrganizationShelfPermission.objects.get(shelf=shelf)
        shelf_permissions.append('all-%d' % organization_shelf_permission.access_level)
    except:
        pass

    for shelf_permission in GroupShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('group-%d-%d' % (shelf_permission.group.id, shelf_permission.access_level))
    
    for shelf_permission in UserShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('user-%d-%d' % (shelf_permission.user.id, shelf_permission.access_level))
    
    return shelf_permissions

@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage_shelf', organization):
        raise Http404
    
    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            auto_sync = form.cleaned_data['auto_sync']
            shelf_icon = form.cleaned_data['shelf_icon']
            permissions = request.POST.getlist('permission')

            shelf = OrganizationShelf.objects.create(organization=organization, name=name, auto_sync=auto_sync, icon=shelf_icon, created_by=request.user)

            _persist_shelf_permissions(request, organization, shelf)

            messages.success(request, u'สร้างชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
        
        shelf_permissions = request.POST.getlist('permission')

    else:
        form = OrganizationShelfForm(initial={'shelf_icon':settings.DEFAULT_SHELF_ICON})
        shelf_permissions = ['all-1']
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':None, 'shelf_type':'create', 'shelf_permissions':shelf_permissions})

@login_required
def edit_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'manage_shelf', organization):
        raise Http404

    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            shelf.name = form.cleaned_data['name']
            shelf.auto_sync = form.cleaned_data['auto_sync']
            shelf.icon = form.cleaned_data['shelf_icon']
            shelf.save()

            _persist_shelf_permissions(request, organization, shelf)

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
        
        shelf_permissions = request.POST.getlist('permission')

    else:
        form = OrganizationShelfForm(initial={'name':shelf.name, 'auto_sync':shelf.auto_sync, 'shelf_icon':shelf.icon})
        shelf_permissions = _extract_shelf_permissions(shelf)
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':shelf, 'shelf_type':'edit', 'shelf_permissions':shelf_permissions})

@login_required
def delete_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'manage_shelf', organization):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            delete_documents = 'delete_documents' in request.POST and request.POST.get('delete_documents') == 'on'

            PublicationShelf.objects.filter(shelf=shelf).delete()
            OrganizationShelfPermission.objects.filter(shelf=shelf).delete()
            GroupShelfPermission.objects.filter(shelf=shelf).delete()
            UserShelfPermission.objects.filter(shelf=shelf).delete()
            
            if delete_documents:
                for publication in Publication.objects.filter(shelves__in=[shelf]):
                    delete_publication(publication)
                
                messages.success(request, u'ลบชั้นหนังสือและไฟล์ในชั้นเรียบร้อย')

            else:
                messages.success(request, u'ลบชั้นหนังสือเรียบร้อย')
            
            shelf.delete()
            return redirect('view_documents', organization_slug=organization.slug)

        else:
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
    
    shelf_documents_count = Publication.objects.filter(shelves__in=[shelf]).count()
    return render(request, 'document/shelf_delete.html', {'organization':organization, 'shelf_documents_count':shelf_documents_count, 'shelf':shelf, 'shelf_type':'delete'})
