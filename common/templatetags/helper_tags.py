# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse
from django.template import NodeList
from django.template import loader

from common import utilities
from common.permissions import can

from accounts.models import UserOrganization
from document.models import Publication

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

# PERMISSION #################################################################

class CanNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, user, actions, parameters):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user = template.Variable(user)
        self.actions = actions.strip(' \"\'')

        self.parameters = {}
        for key in parameters.keys():
            self.parameters[key] = template.Variable(parameters[key])
    
    def render(self, context):
        user = self.user.resolve(context)
        actions = self.actions

        parameters = {}
        for key in self.parameters.keys():
            parameters[key] = self.parameters[key].resolve(context)
        
        if can(user, actions, parameters):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="can")
def do_can(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError('can tag takes user, action name and base object as a required argument')
    
    parameters = {}
    remaining_bits = bits[3:]
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
    
    return CanNode(nodelist_true, nodelist_false, bits[1], bits[2], parameters)

# HTML GENERATOR #################################################################

@register.simple_tag
def generate_organization_menu(user):
    user_organizations = UserOrganization.objects.filter(user=user).order_by('organization__name')

    if len(user_organizations) > 1:
        menus = []
        for user_organization in user_organizations:
            menus.append('<li><a href="%s">%s</a></li>' % (reverse('view_organization_front', args=[user_organization.organization.slug]), user_organization.organization.name))

        return u'<li class="dropdown"><a class="dropdown-toggle" href="#">เปลี่ยนบัญชี</a><ul class="dropdown-menu">%s</ul></li>' % ''.join(menus)
    else:
        return ''

@register.simple_tag
def genetate_publication_category_multiple_checkbox(existing_categories):
    from publisher.models import PublicationCategory

    COLUMN_COUNT = 4
    columns = [[] for i in range(0, COLUMN_COUNT)]

    categories = PublicationCategory.objects.all().order_by('name')
    categories_count = len(categories)

    for i in range(0, categories_count):
        category = categories[i]
        check_html = ' checked="checked"' if existing_categories and category.id in existing_categories else ''
        columns[i % COLUMN_COUNT].append('<li><label for="id_categories_%s"><input type="checkbox" id="id_categories_%s" value="%d" name="categories"%s> %s</label></li>' % (category.slug, category.slug, category.id, check_html, category.name))
    
    htmls = []
    for i in range(0, COLUMN_COUNT):
        # NOTE: You have to change style according to column count
        htmls.append('<div class="checkbox_column"><ul>%s</ul></div>' % ''.join(columns[i]))
    
    return ''.join(htmls)

# MANAGEMENT ################################################################################

@register.simple_tag
def print_organization_status(publisher):
    if publisher.status == 0:
        return u'ปกติ'
    else:
        return u'-- ข้อมูลไม่เพียงพอ --'






# HOWTO: Simple filter

"""
@register.filter(name='filter_name')
def filter_name(datetime):
    return 'string'
"""

# HOWTO: Simple template tag

"""
@register.simple_tag
def template_tag_name():
    return 'string'
"""


# HOWTO: Template Tag with block

"""
class TemplateTagBlockNode(template.Node):
    def __init__(self, nodelist, argument1, argument2):
    	self.nodelist = nodelist
        self.argument1 = template.Variable(argument1)
        self.argument2 = argument2.strip(' \"\'')
    
    def render(self, context):
        argument1 = self.argument1.resolve(context)
        argument2 = self.argument2

        output = self.nodelist.render(context)

        return output

@register.tag(name="template_tag_block")
def do_template_tag_block(parser, token):
    try:
        tag_name, argument1, argument2 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "template_tag_block tag raise ValueError"
    
    nodelist = parser.parse(('end_template_tag_block',))
    parser.delete_first_token()

    return TemplateTagBlockNode(nodelist, argument1, argument2)
"""

# HOWTO: Template Tag with block and else

"""
class TemplateTagBlockElseNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, argument1, argument2):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.argument1 = template.Variable(argument1)
        self.argument2 = argument2.strip(' \"\'')
    
    def render(self, context):
        argument1 = self.argument1.resolve(context)
        argument2 = self.argument2
        
        if True:
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="template_tag_block_else")
def do_template_tag_block_else(parser, token):
    try:
        tag_name, argument1, argument2 = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "template_tag_block_else tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'end_template_tag_block_else'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_template_tag_block_else',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return TemplateTagBlockElseNode(nodelist_true, nodelist_false, argument1, argument2)
"""