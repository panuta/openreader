# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.template import NodeList
from django.template import loader

from django.core.urlresolvers import reverse

from common.permissions import can

from document.models import OrganizationShelf, Document
from publication.models import Publication

# SHELF

@register.simple_tag
def generate_shelf_options(organization):
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        shelf_html.append('<option value="%d">%s</option>' % (shelf.id, shelf.name))
    
    return ''.join(shelf_html)

@register.simple_tag
def generate_shelf_list(user, organization, active_shelf=None):
    if not isinstance(active_shelf, OrganizationShelf):
        active_shelf = None
    
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''

        if can(user, 'edit', organization):
            count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document').count()
        else:
            count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).count()

        shelf_html.append(u'<li class="shelf%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (active_html, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

@register.simple_tag
def print_all_publication_count(user, organization):
    if can(user, 'edit', organization):
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document').count()
    else:
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).count()
    
    return count

class HasShelfNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, organization):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.organization = template.Variable(organization)
    
    def render(self, context):
        organization = self.organization.resolve(context)
        
        if OrganizationShelf.objects.filter(organization=organization).exists():
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="has_shelf")
def do_has_shelf(parser, token):
    try:
        tag_name, organization = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "has_shelf tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'end_has_shelf'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_has_shelf',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return HasShelfNode(nodelist_true, nodelist_false, organization)