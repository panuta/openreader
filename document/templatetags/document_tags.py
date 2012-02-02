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
        shelficon = ' %s' % shelf.icon if shelf.icon else settings.DEFAULT_SHELF_ICON
        count = Publication.objects.filter(shelves__in=[shelf]).count()
        shelf_html.append(u'<li class="shelf%s%s" id="shelf-%d"><a href="%s">%s <span>(%d ไฟล์)</span></a></li>' % (active_html, shelficon, shelf.id, reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

@register.simple_tag
def print_all_publication_count(user, organization): # DONE
    shelves = user.get_profile().get_viewable_shelves(organization)
    return Publication.objects.filter(shelves__in=shelves).order_by('-uploaded_by').count()

@register.simple_tag
def generate_shelf_permission_list(shelf_permissions):
    li_html = []
    for shelf_permission in shelf_permissions:
        permit = shelf_permission.split('-')

        if permit[0] == 'all':
            li_html.append(u'<li>ทุกคนในบริษัทสามารถ%s<span>[ <a href="#">ลบออก</a> ]</span><input type="hidden" name="permission" value="%s"/></li>' % (u'อัพโหลดไฟล์และแก้ไขไฟล์ได้' if permit[1] == '2' else u'ดูไฟล์ได้อย่างเดียว (ยกเว้นผู้ดูแลระบบ)', shelf_permission))
            
        elif permit[0] == 'group':
            group = OrganizationGroup.objects.get(id=permit[1])
            li_html.append(u'<li>กลุ่มผู้ใช้ <em>%s</em> สามารถ%s<span>[ <a href="#">ลบออก</a> ]</span><input type="hidden" name="permission" value="%s"/></li>' % (group.name, u'อัพโหลดไฟล์และแก้ไขไฟล์ได้' if permit[1] == '2' else u'ดูไฟล์ได้อย่างเดียว', shelf_permission))
            
        elif permit[0] == 'user':
            user = User.objects.get(id=permit[1])
            li_html.append(u'<li>ผู้ใช้ <em>%s</em> สามารถ%s<span>[ <a href="#">ลบออก</a> ]</span><input type="hidden" name="permission" value="%s"/></li>' % (user.get_profile().get_fullname(), u'อัพโหลดไฟล์และแก้ไขไฟล์ได้' if permit[1] == '2' else u'ดูไฟล์ได้อย่างเดียว', shelf_permission))
    
    return ''.join(li_html)

@register.simple_tag
def generate_shelf_icons():
    li_html = []
    for icon in settings.SHELF_ICONS:
        li_html.append('<li><a href="#" rel="%s"><img src="%simages/shelficons/24/%s.png" /></a></li>' % (icon, settings.STATIC_URL, icon))

    return ''.join(li_html)
