# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.conf import settings
from django.template import NodeList
from django.template import loader

from django.core.urlresolvers import reverse

from common.permissions import can

from accounts.models import OrganizationGroup
from document.models import SHELF_ACCESS, Publication, OrganizationShelf

@register.simple_tag
def print_publication_tags(publication):
    tag_names = []
    for tag in publication.tags.all():
        tag_names.append('<li>%s</li>' % tag.tag_name)
    
    return '<ul>%s</ul>' % ''.join(tag_names)

# SHELF

@register.simple_tag
def generate_shelf_list(user, organization, active_shelf=None): # DONE
    shelf_html = []
    for shelf in user.get_profile().get_viewable_shelves(organization):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''
        shelficon = ' %s' % shelf.icon if shelf.icon else ''
        count = Publication.objects.filter(shelves__in=[shelf]).count()
        shelf_html.append(u'<li class="shelf%s%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (active_html, shelficon, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
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

@register.simple_tag
def generate_shelf_icons():
    li_html = []
    for icon in settings.SHELF_ICONS:
        li_html.append('<li><a href="#" rel="%s"><img src="%simages/shelficons/24/%s.png" /></a></li>' % (icon, settings.STATIC_URL, icon))

    return ''.join(li_html)
