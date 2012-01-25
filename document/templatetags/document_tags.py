# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.template import NodeList
from django.template import loader

from django.core.urlresolvers import reverse

from common.permissions import can

from accounts.models import OrganizationGroup
from document.models import SHELF_ACCESS, Publication, OrganizationShelf

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
def generate_shelf_list(user, organization, active_shelf=None): # DONE
    shelf_html = []
    for shelf in user.get_profile().get_viewable_shelves(organization):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''
        count = Publication.objects.filter(shelves__in=[shelf]).count()
        shelf_html.append(u'<li class="shelf%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (active_html, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

@register.simple_tag
def print_all_publication_count(user, organization): # DONE
    shelves = user.get_profile().get_viewable_shelves(organization)
    return Publication.objects.filter(shelves__in=shelves).order_by('-uploaded_by').count()

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