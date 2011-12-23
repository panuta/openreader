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
        shelf_html.append('<option value="%d">%s%s</option>' % (shelf.id, shelf.name, u' (ส่วนกลาง)' if shelf.is_shared else ''))
    
    return ''.join(shelf_html)

@register.simple_tag
def generate_shelf_list(user, organization, active_shelf=None):
    if not isinstance(active_shelf, OrganizationShelf):
        active_shelf = None
    
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('-is_shared', 'name'):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''
        private_shelf = ' private-shelf' if not shelf.is_shared else ''

        if can(user, 'edit', organization):
            count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document').count()
        else:
            count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).count()

        shelf_html.append(u'<li class="shelf%s%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (private_shelf, active_html, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

@register.simple_tag
def generate_documents_with_no_shelf_menu(organization, user, shelf_type):
    if can(user, 'edit', organization):
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', shelves=None, publication__uploaded_by=user).count()
    else:
        count = Document.objects.filter(publication__organization=organization, publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED'], shelves=None, publication__uploaded_by=user).count()
    
    if shelf_type == 'none' or count:
        active_html = ' active' if shelf_type == 'none' else ''
        return u'<li class="shelf-none%s"><a href="%s">ไฟล์ที่ยังไม่อยู่ในชั้น <span>(%d ไฟล์)</span></a></li>' % (active_html, reverse('view_documents_with_no_shelf', args=[organization.slug]), count)
    else:
        return ''


@register.simple_tag
def generate_shelf_permission_input(organization, user=None):
    input_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        input_html.append('<span>%s</span><ul><li><input type="radio" name="shelf-%d-permission" /> Can edit</li><li><input type="radio" name="shelf-%d-permission" /> Can view only</li><li><input type="radio" name="shelf-%d-permission" /> No access</li></ul>' % (shelf.id, shelf.id, shelf.id))
    
    return ''.join(input_html)

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