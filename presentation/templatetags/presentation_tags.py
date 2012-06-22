# -*- encoding: utf-8 -*-

from django.conf import settings

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

from domain.models import OrganizationGroup, UserOrganization, UserOrganizationInvitation, OrganizationShelf, OrganizationShelfPermission, GroupShelfPermission

from accounts.permissions import get_backend as get_permission_backend

@register.simple_tag
def print_publication_tags(publication):
    tag_names = []
    for tag in publication.tags.all():
        tag_names.append('<li>%s</li>' % tag.tag_name)

    return '<ul>%s</ul>' % ''.join(tag_names)

# Shelf

@register.simple_tag(takes_context=True)
def generate_shelf_selection(context, user, organization): # USED
    shelf_html = []
    for shelf in get_permission_backend(context.get('request')).get_viewable_shelves(user, organization):
        shelf_html.append(u'<li><a href="%s">%s</a></li>' % (reverse('view_documents_by_shelf', args=[organization.slug, shelf.id]), shelf.name))

    return ''.join(shelf_html)


@register.simple_tag
def shelf_organization_permission_radio(shelf):
    shelf_permission, created = OrganizationShelfPermission.objects.get_or_create(shelf=shelf)

    return '<label><input type="radio" name="all-permission" value="%d"%s/> อัพโหลดและแก้ไขไฟล์ได้</label>\
        <label><input type="radio" name="all-permission" value="%d"%s/> ดูไฟล์ได้อย่างเดียว</label>'% (
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if shelf_permission.access_level == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if shelf_permission.access_level == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
    )


@register.simple_tag
def shelf_group_permission_radio(group, shelf):
    shelf_permission, created = GroupShelfPermission.objects.get_or_create(shelf=shelf, group=group)

    return '<label><input type="radio" name="group-%d-permission" value="%d"%s/> อัพโหลดและแก้ไขไฟล์ได้</label>\
        <label><input type="radio" name="group-%d-permission" value="%d"%s/> ดูไฟล์ได้อย่างเดียว</label>\
        <label><input type="radio" name="group-%d-permission" value="%d"%s/> ไม่สามารถเข้าถึงได้</label>' % (
        group.id,
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if shelf_permission.access_level == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        group.id,
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if shelf_permission.access_level == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
        group.id,
        OrganizationShelf.SHELF_ACCESS['NO_ACCESS'],
        ' checked="checked"' if shelf_permission.access_level == OrganizationShelf.SHELF_ACCESS['NO_ACCESS'] else '',
    )


@register.simple_tag
def shelf_user_permission_radio(user_permission):
    return '<label><input type="radio" name="user-permission-%d" value="%d"%s/> อัพโหลดและแก้ไขไฟล์ได้</label>\
        <label><input type="radio" name="user-permission-%d" value="%d"%s/> ดูไฟล์ได้อย่างเดียว</label>\
        <label><input type="radio" name="user-permission-%d" value="%d"%s/> ไม่สามารถเข้าถึงได้</label>' % (
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['NO_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['NO_ACCESS'] else '',
    )


@register.simple_tag
def generate_shelf_icons():
    li_html = []
    for icon in settings.SHELF_ICONS:
        li_html.append('<li><a href="#" rel="%s"><img src="%simages/shelficons/24/%s.png" /></a></li>' % (icon, settings.STATIC_URL, icon))

    return ''.join(li_html)

# User Management

@register.simple_tag
def print_all_user_count(organization):
    return UserOrganization.objects.filter(organization=organization).count()

@register.simple_tag
def print_active_user_count(organization):
    return UserOrganization.objects.filter(organization=organization, is_active=True).count()

@register.simple_tag
def print_user_group_count(organization):
    return OrganizationGroup.objects.filter(organization=organization).count()

@register.assignment_tag
def return_user_invitation_count(organization):
    return UserOrganizationInvitation.objects.filter(organization=organization).count()