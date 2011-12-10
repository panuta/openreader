# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from common.permissions import can

from document.models import OrganizationShelf, Document
from publication.models import Publication

@register.simple_tag
def generate_shelf_list(user, organization, active_shelf=None):
    if active_shelf in ('all', 'none'):
        active_shelf = None
    
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''

        if can(user, 'edit', organization):
            count = OrganizationShelf.objects.filter(shelf=shelf, publication__publication_type='document').count()
        else:
            count = OrganizationShelf.objects.filter(shelf=shelf, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).count()

        shelf_html.append('<li class="shelf%s"><a href="%s">%s (%d)</a></li>' % (active_html, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

@register.simple_tag
def print_publication_with_no_shelf_count(user, organization):
    if can(user, 'edit', organization):
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves=None).count()
    else:
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED'], shelves=None).count()
    
    return count