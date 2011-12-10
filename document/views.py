# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404
from django.shortcuts import get_object_or_404, redirect, render

from common.permissions import can

from accounts.models import Organization
from publication.models import Publication

#from forms import *
from models import *

@login_required
def view_organization_front(request, organization_slug):
    return redirect('view_documents', organization_slug=organization_slug)

@login_required
def view_documents(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file').order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')

    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'shelf':'all'})

@login_required
def view_documents_by_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', shelves__in=[shelf]).order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', shelves__in=[shelf], status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')
    
    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'shelf':shelf})

@login_required
def view_documents_with_no_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', shelves=None).order_by('-publication__uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', shelves=None, status=Publication.STATUS['PUBLISHED']).order_by('-publication__uploaded')

    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents, 'shelf':'none'})

# SHELF

@login_required
def create_document_shelf(request, organization_slug):
    organization = get_object_or_404(Organization, slug=organization_slug)

    if not can(request.user, 'manage', publisher):
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
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form})

@login_required
def edit_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    shelf = get_object_or_404(OrganizationShelf, pk=shelf_id)

    if shelf.organization.id != organization.id or not can(request.user, 'manage', publisher):
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
    
    return render(request, 'document/shelf_modify.html', {'organization':organization, 'form':form, 'shelf':shelf})

@login_required
def delete_document_shelf(request, organization_slug, shelf_id):
    organization = get_object_or_404(Organization, slug=organization_slug)
    

# DOCUMENT

@login_required
def view_document(request, publication_id):
    pass

@login_required
def edit_document(request, publication_id):
    pass

@login_required
def delete_document(request, publication_id):
    pass

