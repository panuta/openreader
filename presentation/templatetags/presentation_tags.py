# -*- encoding: utf-8 -*-

from django.conf import settings

from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

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
    try:
        shelf_permission = OrganizationShelfPermission.objects.get(shelf=shelf).access_level
    except OrganizationShelfPermission.DoesNotExist:
        shelf_permission = OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS']

    return '<label><input type="radio" name="all-permission" value="%d"%s/> %s</label>\
        <label><input type="radio" name="all-permission" value="%d"%s/> %s</label>'% (
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if shelf_permission == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        _('Can upload and edit files'),
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if shelf_permission == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
        _('Only view file'),
    )


@register.simple_tag
def shelf_group_permission_radio(group, shelf):
    try:
        shelf_permission = GroupShelfPermission.objects.get(shelf=shelf, group=group).access_level
    except GroupShelfPermission.DoesNotExist:
        shelf_permission = OrganizationShelf.SHELF_ACCESS['NO_ACCESS']

    return '<label><input type="radio" name="group-permission-%d" value="%d"%s/> %s</label>\
        <label><input type="radio" name="group-permission-%d" value="%d"%s/> %s</label>\
        <label><input type="radio" name="group-permission-%d" value="%d"%s/> %s</label>' % (
        group.id,
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if shelf_permission == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        _('Can upload and edit files'),
        group.id,
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if shelf_permission == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
        _('Only view file'),
        group.id,
        OrganizationShelf.SHELF_ACCESS['NO_ACCESS'],
        ' checked="checked"' if shelf_permission == OrganizationShelf.SHELF_ACCESS['NO_ACCESS'] else '',
        _('Cannot access to'),
    )


@register.simple_tag
def shelf_user_permission_radio(user_permission):
    return '<label><input type="radio" name="user-permission-%d" value="%d"%s/> %s</label>\
        <label><input type="radio" name="user-permission-%d" value="%d"%s/> %s</label>\
        <label><input type="radio" name="user-permission-%d" value="%d"%s/> %s</label>' % (
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS'] else '',
        _('Can upload and edit files'),
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS'] else '',
        _('Only view file'),
        user_permission.user.id,
        OrganizationShelf.SHELF_ACCESS['NO_ACCESS'],
        ' checked="checked"' if user_permission.access_level == OrganizationShelf.SHELF_ACCESS['NO_ACCESS'] else '',
        _('Cannot access to'),
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