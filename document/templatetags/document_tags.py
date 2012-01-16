# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.template import NodeList
from django.template import loader

from django.core.urlresolvers import reverse

from common.permissions import can

from accounts.models import OrganizationGroup
from document.models import SHELF_ACCESS, OrganizationShelf, Document
from publication.models import Publication

# Used in create/edit shelf page
@register.simple_tag
def shelf_permissions_radio_table(organization, permissions=None):
    table_html = []
    for group in OrganizationGroup.objects.filter(organization=organization).order_by('name'):

        check_publish = ''
        check_view = ''
        check_no = ''

        if permissions:
            if permissions[group.id] == SHELF_ACCESS['PUBLISH_ACCESS'] or permissions[group.id] == 'publish':
                check_publish = 'checked="checked"'
                
            elif permissions[group.id] == SHELF_ACCESS['VIEW_ACCESS'] or permissions[group.id] == 'view':
                check_view = 'checked="checked"'

            elif permissions[group.id] == SHELF_ACCESS['NO_ACCESS'] or permissions[group.id] == 'no':
                check_no = 'checked="checked"'

        table_html.append(u'<tr class="permission_row"><td>%s</td><td><label><input type="radio" name="group_access-%d" value="publish" %s/> อัพโหลดและแก้ไข</label></td><td><label><input type="radio" name="group_access-%d" value="view" %s/> ดูอย่างเดียว</label></td><td><label><input type="radio" name="group_access-%d" value="no" %s/> ไม่สามารถเข้าถึงได้</label></td></tr>' % (group.name, group.id, check_publish, group.id, check_view, group.id, check_no))
    
    return ''.join(table_html)

# SHELF

@register.simple_tag
def generate_shelf_options(organization):
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        shelf_html.append('<option value="%d">%s%s</option>' % (shelf.id, shelf.name, u' (ส่วนกลาง)' if shelf.is_shared else ''))
    
    return ''.join(shelf_html)

@register.simple_tag
def generate_shelf_list(user, organization, active_shelf=None): # EDITED
    shelf_html = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        access_level = user.get_profile().get_shelf_access(shelf)
        print access_level

        if access_level > SHELF_ACCESS['NO_ACCESS']:
            active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''
            restricted_shelf = ' restricted-shelf' if access_level == SHELF_ACCESS['VIEW_ACCESS'] else ''

            if can(user, 'edit', organization):
                count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document').count()
            else:
                count = Document.objects.filter(shelves__in=[shelf], publication__publication_type='document', publication__status=Publication.STATUS['PUBLISHED']).count()

            shelf_html.append(u'<li class="shelf%s%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (restricted_shelf, active_html, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
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