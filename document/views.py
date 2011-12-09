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

def view_document_front(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)

    if not can(request.user, 'view', organization):
        raise Http404
    
    if can(request.user, 'edit', organization):
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file').order_by('-uploaded')
    else:
        documents = Document.objects.filter(publication__organization=organization, publication__publication_type='file', status=Publication.STATUS['PUBLISHED']).order_by('-uploaded')

    return render(request, 'document/documents.html', {'organization':organization, 'documents':documents})

