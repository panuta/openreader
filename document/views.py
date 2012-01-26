# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from openreader.http import Http403

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
            'url': reverse('view_document', args=[publication.uid])
        })
    
    return render(request, 'document/documents_upload.html', {'organization':organization, 'shelf':shelf, 'shelf_type':'shelf'})
    


@login_required
def upload_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    return _upload_documents(request, organization)

"""
@login_required
def upload_documents_to_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, id=shelf_id)

    if shelf.organization.id != organization.id:
        raise Http404

    return _upload_documents(request, organization, shelf)
"""

def _upload_documents(request, organization, shelf=None):
    if not can(request.user, 'edit', {'organization':organization}):
        raise Http404

    if request.method == 'POST':
        file = request.FILES[u'file']

        if not file:
            return response_json_error('file-missing')
        
        uploading_file = UploadedFile(file)

        publication = publication_functions.upload_publication(request, 'document', uploading_file, organization)
        document = Document.objects.create(publication=publication)

        if shelf:
            DocumentShelf.objects.create(document=document, shelf=shelf, created_by=request.user)
            document.publication.status = Publication.STATUS['UNPUBLISHED']
            document.publication.save()

        return response_json_success({
            'uid': str(publication.uid),
            'title': publication.title,
            'size': uploading_file.file.size,
            'shelf':shelf.id if shelf else '',
            'url': reverse('view_document', args=[publication.uid])
        })

    else:
        raise Http404

@login_required
def finishing_upload_documents(request, organization_slug):
    if request.method == 'POST':
        organization = get_object_or_404(Organization, slug=organization_slug)

        uid = request.POST.get('uid')
        title = request.POST.get('title')
        shelf_id = request.POST.get('shelf_id')

        if not can(request.user, 'edit', {'organization':organization}):
            return HttpResponseBadRequest('access-denied')

        try:
            document = Document.objects.get(publication__uid=uid)
        except Document.DoesNotExist:
            return HttpResponseBadRequest('document-not-found')
        
        if document.publication.organization.id != organization.id:
            return HttpResponseBadRequest('document-not-found')
        
        if not title:
            return HttpResponseBadRequest('missing-parameters')
        
        try:
            shelf = OrganizationShelf.objects.get(id=shelf_id)
        except OrganizationShelf.DoesNotExist:
            return HttpResponseBadRequest('shelf-not-found')
        
        if shelf.organization.id != organization.id:
            return HttpResponseBadRequest('shelf-not-found')
        
        DocumentShelf.objects.create(shelf=shelf, document=document, created_by=request.user)

        document.publication.title = title
        document.publication.status = Publication.STATUS['UNPUBLISHED']
        document.publication.save()
        
        return response_json({
            'uid':str(document.publication.uid),
            'title':document.publication.title,
            'shelf_name':shelf.name if shelf_id else '',
            'uploaded':format_abbr_datetime(document.publication.uploaded),
            'status':document.publication.get_status_text(),
            'view_url':reverse('view_document', args=[document.publication.uid]),
            'edit_url':reverse('edit_document', args=[document.publication.uid]),
        })
    
    raise Http404

# SHELF

def _persist_shelf_permissions(request, organization, shelf):
    all_access_permission = request.POST.get('all_access')

    if all_access_permission == 'publish':
        for group in OrganizationGroup.objects.filter(organization=organization):
            ShelfPermission.objects.create(group=group, shelf=shelf, access_level=SHELF_ACCESS['PUBLISH_ACCESS'], created_by=request.user)
        
    elif all_access_permission == 'view':
        for group in OrganizationGroup.objects.filter(organization=organization):
            ShelfPermission.objects.create(group=group, shelf=shelf, access_level=SHELF_ACCESS['VIEW_ACCESS'], created_by=request.user)

    else:
        shelf_permissions = {}
        for item in request.POST.keys():
            if item[:13] == 'group_access-':
                group_id = item.split('-')[1]
                try:
                    group = OrganizationGroup.objects.get(id=group_id, organization=organization)
                except:
                    pass
                else:
                    access_lebel_name = request.POST[item]

                    if access_lebel_name == 'publish':
                        access_level = SHELF_ACCESS['PUBLISH_ACCESS']
                    elif access_lebel_name == 'view':
                        access_level = SHELF_ACCESS['VIEW_ACCESS']
                    else:
                        access_level = SHELF_ACCESS['NO_ACCESS']
                        
                    shelf_permissions[group.id] = access_level

        for group in OrganizationGroup.objects.filter(organization=organization):
            access_level = shelf_permissions.get(group.id, SHELF_ACCESS['NO_ACCESS'])
            ShelfPermission.objects.create(group=group, shelf=shelf, access_level=access_level, created_by=request.user)

@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'admin', {'organization':organization}):
        raise Http403
    
    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            auto_sync = bool(request.POST.get('auto_sync'))

            shelf = OrganizationShelf.objects.create(organization=organization, name=name, created_by=request.user, auto_sync=auto_sync)

            _persist_shelf_permissions(request, organization, shelf)
            
            messages.success(request, u'เพิ่มชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
        
        all_access_permission = request.POST.get('all_access')

        shelf_permissions = {}
        for group in OrganizationGroup.objects.filter(organization=organization):
            shelf_permissions[group.id] = request.POST.get('group_access-%d' % group.id)

    else:
        form = OrganizationShelfForm()
        all_access_permission = ''
        shelf_permissions = {}
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':None, 'shelf_type':'create', 'all_access_permission':all_access_permission, 'shelf_permissions':shelf_permissions})

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
            auto_sync = bool(request.POST.get('auto_sync'))
            shelf.auto_sync = auto_sync
            shelf.save()

            ShelfPermission.objects.filter(shelf=shelf).delete()

            _persist_shelf_permissions(request, organization, shelf)

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

    else:
        shelf_permissions = {}
        permission_list = []
        for permission in ShelfPermission.objects.filter(shelf=shelf):
            shelf_permissions[permission.group.id] = permission.access_level
            permission_list.append(permission.access_level)
        
        all_access_permission = ''

        if len(set(permission_list)) <= 1:
            if permission_list[0] == SHELF_ACCESS['VIEW_ACCESS']:
                all_access_permission = 'view'
            
            if permission_list[0] == SHELF_ACCESS['PUBLISH_ACCESS']:
                all_access_permission = 'publish'

        print shelf_permissions
        form = OrganizationShelfForm(initial={'name':shelf.name})
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':shelf, 'shelf_type':'edit', 'shelf_permissions':shelf_permissions, 'all_access_permission':all_access_permission})

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

@login_required
def move_document_to_shelf(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        shelf_id = request.POST.get('shelf_id')

        try:
            document = Document.objects.get(publication__uid=uid)
        except Document.DoesNotExist:
            return HttpResponseBadRequest('document-not-found')
        
        if not can(request.user, 'edit', {'organization':document.publication.organization}):
            return HttpResponseBadRequest('access-denied')
        
        try:
            shelf = OrganizationShelf.objects.get(id=shelf_id)
        except OrganizationShelf.DoesNotExist:
            return HttpResponseBadRequest('shelf-not-found')
        
        DocumentShelf.objects.create(shelf=shelf, document=document, created_by=request.user)
        
        document.publication.status = Publication.STATUS['UNPUBLISHED']
        document.publication.save()

        return response_json({
            'uid':str(document.publication.uid),
            'shelf_name':shelf.name,
            'edit_url':reverse('edit_document', args=[document.publication.uid]),
        })

# DOCUMENT

@login_required
def view_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization

    if not can(request.user, 'view', {'organization':organization}):
        raise Http403
    
    return render(request, 'document/document_view.html', {'organization':organization, 'publication':publication})

@logged_in_or_basicauth()
def download_publication(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)

    if publication.status == Publication.STATUS['UNFINISHED'] and publication.uploaded_by != request.user:
        raise Http403

    from publication.views import download_publication
    return download_publication(request, publication)

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

