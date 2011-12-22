# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import UploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import simplejson

from common.permissions import can
from common.shortcuts import response_json, response_json_success, response_json_error
from common.utilities import format_abbr_datetime

from accounts.models import Organization
from publication.models import Publication, PublicationNotice

from publication import functions as publication_functions

from forms import *
from models import *

def _organization_statistics(organization):
    document_count = Publication.objects.filter(organization=organization, publication_type='document', status=Publication.STATUS['PUBLISHED']).count()
    shelf_count = OrganizationShelf.objects.filter(organization=organization).count()

    return {'template_name':'document/organization_statistics.html', 'document_count':document_count, 'shelf_count':shelf_count}

@login_required
def view_organization_front(request, organization_slug):
    return redirect('view_documents', organization_slug=organization_slug)

def _no_shelf_count(user, organization):
    if can(user, 'edit', organization):
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves=None).count()
    else:
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED'], shelves=None).count()
    
    return count

@login_required
def view_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document').order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')
    
    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'no_shelf_count':_no_shelf_count(request.user, organization), 'shelf':None, 'shelf_type':'all'})

@login_required
def view_documents_by_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf]).order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf], publication__status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')
    
    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'no_shelf_count':_no_shelf_count(request.user, organization), 'shelf':shelf, 'shelf_type':'shelf'})

@login_required
def view_documents_with_no_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves=None).order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves=None, publication__status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')

    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'no_shelf_count':_no_shelf_count(request.user, organization), 'shelf':None, 'shelf_type':'none'})

@login_required
def upload_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)
    return _upload_documents(request, organization)

@login_required
def upload_documents_to_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, id=shelf_id)

    if shelf.organization.id != organization.id:
        raise Http404

    return _upload_documents(request, organization, shelf)

def _upload_documents(request, organization, shelf=None):
    if not can(request.user, 'edit', organization):
        raise Http404

    if request.method == 'POST':
        file = request.FILES[u'file']

        if not file:
            return response_json_error('file-missing')
        
        uploading_file = UploadedFile(file)

        try:
            publication = publication_functions.upload_publication(request, 'document', uploading_file, organization)
            document = Document.objects.create(publication=publication)
            publication.status = Publication.STATUS['UNPUBLISHED']
        except:
            import sys
            print sys.exc_info()

        if shelf:
            DocumentShelf.objects.create(document=document, shelf=shelf, created_by=request.user)

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

        if not can(request.user, 'edit', organization):
            return HttpResponseBadRequest('access-denied')

        try:
            document = Document.objects.get(publication__uid=uid)
        except Document.DoesNotExist:
            return HttpResponseBadRequest('document-not-found')
        
        if document.publication.organization.id != organization.id:
            return HttpResponseBadRequest('document-not-found')
        
        if not title:
            return HttpResponseBadRequest('missing-parameters')
        
        document.publication.title = title
        document.publication.status = Publication.STATUS['UNPUBLISHED']
        document.publication.save()

        if shelf_id:
            try:
                shelf = OrganizationShelf.objects.get(id=shelf_id)
            except OrganizationShelf.DoesNotExist:
                return HttpResponseBadRequest('shelf-not-found')
            
            if shelf.organization.id != organization.id:
                return HttpResponseBadRequest('shelf-not-found')
            
            DocumentShelf.objects.create(shelf=shelf, document=document, created_by=request.user)
        
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

@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']

            shelf = OrganizationShelf.objects.create(organization=organization, name=name, description=description, created_by=request.user)

            messages.success(request, u'เพิ่มชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

    else:
        form = OrganizationShelfForm()
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'no_shelf_count':_no_shelf_count(request.user, organization), 'form':form, 'shelf':None, 'shelf_type':'create'})

@login_required
def edit_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        form = OrganizationShelfForm(request.POST)
        if form.is_valid():
            shelf.name = form.cleaned_data['name']
            shelf.description = form.cleaned_data['description']
            shelf.save()

            messages.success(request, u'แก้ไขชั้นหนังสือเรียบร้อย')
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)

    else:
        form = OrganizationShelfForm(initial={'name':shelf.name, 'description':shelf.description})
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'no_shelf_count':_no_shelf_count(request.user, organization), 'form':form, 'shelf':shelf, 'shelf_type':'edit'})

@login_required
def delete_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'manage', organization):
        raise Http404
    
    if request.method == 'POST':
        if 'submit-delete' in request.POST:
            delete_documents = 'delete_documents' in request.POST and request.POST.get('delete_documents') == 'on'
            
            if delete_documents:
                for document in Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf]):
                    publication_functions.delete_publication(document.publication)
                
                DocumentShelf.objects.filter(shelf=shelf).delete()
                Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves__in=[shelf]).delete()
                
                messages.success(request, u'ลบชั้นหนังสือและไฟล์ในชั้นเรียบร้อย')

            else:
                messages.success(request, u'ลบชั้นหนังสือเรียบร้อย')
            
            shelf.delete()
            return redirect('view_documents', organization_slug=organization.slug)

        else:
            return redirect('view_documents_by_shelf', organization_slug=organization.slug, shelf_id=shelf.id)
    
    shelf_documents_count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document').count()
    return render(request, 'document/shelf_delete.html', {'organization':organization, 'no_shelf_count':_no_shelf_count(request.user, organization), 'shelf_documents_count':shelf_documents_count, 'shelf':shelf, 'shelf_type':'delete'})

# DOCUMENT

@login_required
def view_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization
    document = publication.document

    if not can(request.user, 'view', organization):
        raise Http404
    
    shelves = DocumentShelf.objects.filter(document=document)

    return render(request, 'document/document_view.html', {'organization':organization, 'document':document, 'shelves':shelves})

@login_required
def edit_document(request, publication_uid):
    publication = get_object_or_404(Publication, uid=publication_uid)
    organization = publication.organization
    document = publication.document

    if not can(request.user, 'edit', organization):
        raise Http404
    
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

    if not can(request.user, 'edit', organization):
        raise Http404
    
    return render(request, 'document/document_delete.html', {'organization':organization, 'document':document})

