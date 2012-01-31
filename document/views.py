# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from http import Http403

from private_files.views import get_file as private_files_get_file
from httpauth import logged_in_or_basicauth

from common.permissions import can
from common.shortcuts import response_json, response_json_success, response_json_error
from common.utilities import format_abbr_datetime

from accounts.models import Organization, UserOrganization, OrganizationGroup

from forms import *
from functions import *
from models import *

@login_required
def view_organization_front(request, organization_slug):
    return redirect('view_documents', organization_slug=organization_slug)

@login_required
def view_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', {'organization':organization}):
        raise Http403
    
    shelves = request.user.get_profile().get_viewable_shelves(organization)
    publications = Publication.objects.filter(shelves__in=shelves).order_by('-uploaded')
    return render(request, 'document/documents.html', {'organization':organization, 'publications':publications, 'shelf':None, 'shelf_type':'all'})

@login_required
def view_documents_by_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'view', {'organization':organization}):
        raise Http403
    
    publications = Publication.objects.filter(organization=organization, shelves__in=[shelf]).order_by('-uploaded')
    return render(request, 'document/documents.html', {'organization':organization, 'publications':publications, 'shelf':shelf, 'shelf_type':'shelf'})

# UPLOAD DOCUMENT
######################################################################################################################################################

@login_required
def upload_documents_to_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'upload_shelf', {'organization':organization, 'shelf':shelf}):
        raise Http403
    
    if request.method == 'POST':
        file = request.FILES[u'file']

        if not file:
            return response_json_error('file-missing')
        
        uploading_file = UploadedFile(file)

        publication = upload_publication(request, uploading_file, organization)
        PublicationShelf.objects.create(publication=publication, shelf=shelf, created_by=request.user)

        return response_json_success({
            'uid': str(publication.uid),
            'title': publication.title,
            'size': uploading_file.file.size,
            'shelf':shelf.id if shelf else '',
            'uploaded':format_abbr_datetime(publication.uploaded),
            'download_url': reverse('download_publication', args=[publication.uid])
        })
    
    return render(request, 'document/documents_upload.html', {'organization':organization, 'shelf':shelf, 'shelf_type':'shelf'})

# DOWNLOAD DOCUMENT
######################################################################################################################################################

@logged_in_or_basicauth()
def download_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    can_download = False
    for shelf in publication.shelves.all():
        if request.user.get_profile().get_shelf_access(shelf) >= SHELF_ACCESS['VIEW_ACCESS']:
            can_download = True

    if not can_download:
        raise Http403
    
    return private_files_get_file(request, 'document', 'Publication', 'uploaded_file', str(publication.id), '%s.%s' % (publication.original_file_name, publication.file_ext))

# EDIT DOCUMENT
######################################################################################################################################################

@login_required
def ajax_edit_publication(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if request.method == 'POST':
        publication_uid = request.POST.get('uid')
        title = request.POST.get('title')
        description = request.POST.get('description')
        tag_names = request.POST.getlist('tags[]')

        try:
            publication = Publication.objects.get(uid=publication_uid)
        except Publication.DoesNotExist:
            return response_json_error('invalid-publication')
        
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

    else:
        raise Http404

@login_required
def ajax_add_publications_tag(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if request.method == 'POST':
        publication_uids = request.POST.getlist('publication[]')
        tag_name = request.POST.get('tag')

        if tag_name:
            try:
                tag = OrganizationTag.objects.get(organization=organization, tag_name=tag_name)
            except OrganizationTag.DoesNotExist:
                tag = OrganizationTag.objects.create(organization=organization, tag_name=tag_name)

            for publication_uid in publication_uids:
                try:
                    publication = Publication.objects.get(uid=publication_uid)
                except Publication.DoesNotExist:
                    continue
                
                PublicationTag.objects.get_or_create(publication=publication, tag=tag)
            
            return response_json_success()
        else:
            return response_json_error('missing-parameter')

    else:
        raise Http404

@login_required
def ajax_query_document_tags(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    term = request.GET.get('term')

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

    organization_shelf_permission = OrganizationShelfPermission.objects.get(shelf=shelf)
    shelf_permissions.append('all-%d' % organization_shelf_permission.access_level)

    for shelf_permission in GroupShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('group-%d-%d' % (shelf_permission.group.id, shelf_permission.access_level))
    
    for shelf_permission in UserShelfPermission.objects.filter(shelf=shelf):
        shelf_permissions.append('user-%d-%d' % (shelf_permission.user.id, shelf_permission.access_level))
    
    return shelf_permissions

@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http403
    
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

    if shelf.organization.id != organization.id or not can(request.user, 'admin', {'organization':organization}):
        raise Http403
    
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

    if shelf.organization.id != organization.id or not can(request.user, 'admin', {'organization':organization}):
        raise Http403
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            delete_documents = 'delete_documents' in request.POST and request.POST.get('delete_documents') == 'on'

            DocumentShelf.objects.filter(shelf=shelf).delete()
            ShelfPermission.objects.filter(shelf=shelf).delete()
            
            if delete_documents:
                for document in Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf]):
                    publication_functions.delete_publication(document.publication)
                
                Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf]).delete()

                messages.success(request, u'ลบชั้นหนังสือและไฟล์ในชั้นเรียบร้อย')

            else:
                messages.success(request, u'ลบชั้นหนังสือเรียบร้อย')
            
            shelf.delete()
            return redirect('view_documents', organization_slug=organization.slug)

        else:
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
    
    shelf_documents_count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document').count()
    return render(request, 'document/shelf_delete.html', {'organization':organization, 'shelf_documents_count':shelf_documents_count, 'shelf':shelf, 'shelf_type':'delete'})

# DOCUMENT

@login_required
def view_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization

    if not can(request.user, 'view', {'organization':organization}):
        raise Http403
    
    return render(request, 'document/document_view.html', {'organization':organization, 'publication':publication})

@login_required
def edit_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization

    if not can(request.user, 'edit', {'organization':organization}):
        raise Http403
    
    if request.method == 'POST':
        form = EditFilePublicationForm(request.POST, organization=organization)
        if form.is_valid():
            publication.title = form.cleaned_data['title']
            publication.description = form.cleaned_data['description']
            publication.save()

            new_shelves = set(form.cleaned_data['shelves']) # OrganizationShelf model

            old_shelves = set()
            for shelf in document.shelves.all():
                old_shelves.add(shelf)

            creating_shelves = new_shelves.difference(old_shelves)
            removing_shelves = old_shelves.difference(new_shelves)

            for shelf in creating_shelves:
                DocumentShelf.objects.create(document=document, shelf=shelf, created_by=request.user)
            
            if creating_shelves and publication.status == Publication.STATUS['UNFINISHED']:
                publication.status = Publication.STATUS['UNPUBLISHED']
                publication.save()

            DocumentShelf.objects.filter(document=document, shelf__in=removing_shelves).delete()
            
            messages.success(request, u'แก้ไขรายละเอียดเรียบร้อย')
            if request.POST.get('from_page'):
                return redirect(request.POST.get('from_page'))

            return redirect('view_document', publication.uid)

    else:
        form = EditFilePublicationForm(organization=organization, initial={'title':publication.title, 'description':publication.description, 'shelves':document.shelves.all(), 'from_page':request.GET.get('from')})
    
    return render(request, 'document/document_edit.html', {'organization':organization, 'document':document, 'form':form})

@login_required
def delete_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization
    document = publication.document

    if not can(request.user, 'edit', {'organization':organization}):
        raise Http403
    
    if document.publication.status == Publication.STATUS['UNFINISHED'] and document.publication.uploaded_by != request.user:
        raise Http404
    
    return render(request, 'document/document_delete.html', {'organization':organization, 'document':document})

