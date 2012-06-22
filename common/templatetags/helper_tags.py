# -*- encoding: utf-8 -*-

from django import template
from django.template.base import TemplateSyntaxError

register = template.Library()

from django.core.urlresolvers import reverse
from django.template import NodeList

from common import utilities
from accounts.permissions import get_backend as get_permission_backend

from domain.models import UserOrganization

# DATE TIME #################################################################

@register.filter(name='format_datetime')
def format_datetime(datetime):
    return utilities.format_full_datetime(datetime)

@register.filter(name='format_abbr_datetime')
def format_abbr_datetime(datetime):
    return utilities.format_abbr_datetime(datetime)

@register.filter(name='format_date')
def format_date(datetime):
    return utilities.format_full_date(datetime)

@register.filter(name='format_abbr_date')
def format_abbr_date(datetime):
    return utilities.format_abbr_date(datetime)

# FILTERS #################################################################

@register.filter(name='file_size')
def humanize_file_size(size_in_byte):
    return utilities.humanize_file_size(size_in_byte)

# PERMISSION #################################################################

class CanNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, user, action, organization, parameters):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user = template.Variable(user)
        self.action = action.strip(' \"\'')
        self.organization = template.Variable(organization)

        self.parameters = {}
        for key in parameters.keys():
            self.parameters[key] = template.Variable(parameters[key])
    
    def render(self, context):
        user = self.user.resolve(context)
        permissions = self.action.split(',')
        organization = self.organization.resolve(context)
        permission_backend = get_permission_backend(context['request'])

        parameters = {}
        for key in self.parameters.keys():
            parameters[key] = self.parameters[key].resolve(context)

        if self._has_any_permission(permission_backend, permissions, user, organization, parameters):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

    def _has_any_permission(self, backend, permissions, user, organization, parameters):
        for permission in permissions:
            if hasattr(backend, permission):
                if getattr(backend, permission)(user, organization, parameters):
                    return True
                else:
                    continue
        return False

@register.tag(name="can")
def do_can(parser, token):
    bits = token.split_contents()
    if len(bits) < 4:
        raise TemplateSyntaxError('can tag takes user, action name and base object as a required argument')
    
    parameters = {}
    remaining_bits = bits[4:]
    while remaining_bits:
        option = remaining_bits.pop(0)

        try:
            (key, value) = option.split('=')
            parameters[key] = value
        except:
            pass

    nodelist_true = parser.parse(('else', 'endcan'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endcan',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return CanNode(nodelist_true, nodelist_false, bits[1], bits[2], bits[3], parameters)

# HTML GENERATOR #################################################################

@register.simple_tag
def generate_organization_menu(user):
    user_organizations = UserOrganization.objects.filter(user=user, is_active=True).order_by('organization__name')

    if len(user_organizations) > 1:
        menus = []
        for user_organization in user_organizations:
            menus.append('<li><a href="%s">%s%s</a></li>' % (reverse('view_organization_front', args=[user_organization.organization.slug]), '%s ' % user_organization.organization.prefix if user_organization.organization.prefix else '', user_organization.organization.name))

        return u'<li class="dropdown" id="switch_org_menu"><a class="dropdown-toggle nav_top_link" data-toggle="dropdown" href="#switch_org_menu">เปลี่ยนบัญชี <b class="caret"></b></a><ul class="dropdown-menu">%s</ul></li>' % ''.join(menus)
    else:
        return ''


# MANAGEMENT ################################################################################

@register.simple_tag
def print_organization_status(publisher):
    if publisher.status == 0:
        return u'ปกติ'
    else:
        return u'-- ข้อมูลไม่เพียงพอ --'
