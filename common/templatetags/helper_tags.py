# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse
from django.template import NodeList
from django.template import loader

from common import utilities
from common.permissions import can
from common.modules import *

from accounts.models import UserPublisher
from publisher.models import Publication, PublisherModule, PublisherShelf, PublicationShelf, Module, PublicationNotice


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
    def __init__(self, nodelist_true, nodelist_false, user, action, object):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.user = template.Variable(user)
        self.action = action.strip(' \"\'')
        self.object = template.Variable(object)
    
    def render(self, context):
        user = self.user.resolve(context)
        object = self.object.resolve(context)
        action = self.action

        if can(user, action, object):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="can")
def do_can(parser, token):
    try:
        tag_name, user, action, object = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "can tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'endcan'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endcan',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return CanNode(nodelist_true, nodelist_false, user, action, object)

# SHELF #################################################################

class HasPublisherShelfNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, publisher):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.publisher = template.Variable(publisher)
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        
        if PublisherShelf.objects.filter(publisher=publisher).exists():
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="has_publisher_shelf")
def do_has_publisher_shelf(parser, token):
    try:
        tag_name, publisher = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "has_publisher_shelf tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'end_has_publisher_shelf'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_has_publisher_shelf',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return HasPublisherShelfNode(nodelist_true, nodelist_false, publisher)

# UPLOAD #################################################################

class JustFinishingUploadNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    
    def render(self, context):
        request = context.get('request')
        success_list = request.session.get('finishing_upload_success')

        existing_publications = context.get('publications')

        if success_list:
            context['publications'] = success_list
            output = self.nodelist.render(context)
        else:
            output = ''
        
        request.session['finishing_upload_success'] = []
        context['publications'] = existing_publications
        return output

@register.tag(name="if_just_finishing_upload")
def do_if_just_finishing_upload(parser, token):
    try:
        tag_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "if_just_finishing_upload tag raise ValueError"
    
    nodelist = parser.parse(('endif',))
    parser.delete_first_token()

    return JustFinishingUploadNode(nodelist)

# HTML GENERATOR #################################################################

@register.simple_tag
def generate_top_menu(publisher, active_menu):
    publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication').order_by('created')

    menu_html = ''
    for publisher_module in publisher_modules:
        active_html = ' class="active"' if active_menu == publisher_module.module.module_name else ''
        menu_html = menu_html + '<li%s><a href="%s">%s</a></li>' % (active_html, reverse(publisher_module.module.front_page_url, args=[publisher.id]), publisher_module.module.title)
    
    return menu_html

@register.simple_tag
def generate_publisher_menu(user):
    user_publishers = UserPublisher.objects.filter(user=user).order_by('publisher__name')

    if len(user_publishers) > 1:
        menus = []
        for user_publisher in user_publishers:
            menus.append('<li><a href="%s">%s</a></li>' % (reverse('view_publisher_dashboard', args=[user_publisher.publisher.id]), user_publisher.publisher.name))

        return u'<li class="dropdown"><a class="dropdown-toggle" href="#">เปลี่ยนสำนักพิมพ์</a><ul class="dropdown-menu">%s</ul></li>' % ''.join(menus)
    else:
        return ''

@register.simple_tag
def print_publication_status(publication):
    status = []

    if publication.status == Publication.STATUS['UPLOADED']:
        return u'<span class="unfinished">ยังกรอกข้อมูลไม่ครบ</span>'
    
    elif publication.status == Publication.STATUS['SCHEDULED']:
        
        if publication.is_processing:
            return u'<span class="scheduled">ไฟล์กำลังประมวลผล และตั้งเวลาเผยแพร่ วันที่ %s</span>' % (utilities.format_abbr_datetime(publication.web_scheduled))
        
        else:
            return u'<span class="scheduled">ตั้งเวลาเผยแพร่ วันที่ %s</span>' % (utilities.format_abbr_datetime(publication.web_scheduled))
    
    elif publication.status == Publication.STATUS['UNPUBLISHED']:
        if publication.is_processing:

            if PublicationNotice.objects.filter(publication=publication, notice=PublicationNotice.NOTICE['PUBLISH_WHEN_READY']):
                return u'<span class="unpublished">ไฟล์กำลังประมวลผล และจะเผยแพร่ทันทีที่ประมวลผลเสร็จ</span>'

            else:
                return u'<span class="unpublished">ไฟล์กำลังประมวลผล และยังไม่เผยแพร่</span>'
            
        else:
            return u'<span class="unpublished">ยังไม่เผยแพร่</span>'

    elif publication.status == Publication.STATUS['PUBLISHED']:
        return u'<span class="published">เผยแพร่แล้ว วันที่ %s</span>' % (utilities.format_abbr_datetime(publication.web_published))
    
    return ''

@register.simple_tag
def generate_publication_actions(publication):
    # TODO Check permission
    
    if publication.status == Publication.STATUS['UPLOADED']:
        return u'<a href="%s" class="small btn"><span>กรอกข้อมูลต่อ</span></a>' % reverse('finishing_upload_publication', args=[publication.id])
    
    elif publication.status == Publication.STATUS['SCHEDULED']:
        return u'<a href="%s" class="small btn action-schedule"><span>ตั้งเวลาใหม่</span></a><a href="%s" class="link">แก้ไขรายละเอียด</a>' % (reverse('set_publication_schedule', args=[publication.id]), reverse('edit_publication', args=[publication.id]))

    elif publication.status == Publication.STATUS['UNPUBLISHED']:
        if publication.is_processing:
            return u'<a href="%s" class="small btn action-schedule"><span>ตั้งเวลาเผยแพร่</a></a><a href="%s" class="small btn action-publish"><span>เผยแพร่ทันทีที่ประมวลผลเสร็จ</span></a><a href="%s" class="link">แก้ไขรายละเอียด</a>' % (reverse('set_publication_schedule', args=[publication.id]), reverse('set_publication_published', args=[publication.id]), reverse('edit_publication', args=[publication.id]))
        else:
            return u'<a href="%s" class="small btn action-schedule"><span>ตั้งเวลาเผยแพร่</a></a><a href="%s" class="small btn action-publish"><span>เผยแพร่ทันที</span></a><a href="%s" class="link">แก้ไขรายละเอียด</a>' % (reverse('set_publication_schedule', args=[publication.id]), reverse('set_publication_published', args=[publication.id]), reverse('edit_publication', args=[publication.id]))
    
    elif publication.status == Publication.STATUS['PUBLISHED']:
        return u'<a href="%s" class="link">แก้ไขรายละเอียด</a>' % reverse('edit_publication', args=[publication.id])
    
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

@register.simple_tag
def generate_shelf_list(user, publisher, module, url, active_shelf=None):
    shelf_html = []
    for shelf in PublisherShelf.objects.filter(publisher=publisher).order_by('name'):
        active_html = ' active' if active_shelf and active_shelf.id == shelf.id else ''

        if can(user, 'edit', publisher):
            count = PublicationShelf.objects.filter(shelf=shelf, publication__publication_type=module).count()
        elif can(user, 'edit', publisher):
            count = PublicationShelf.objects.filter(shelf=shelf, publication__publication_type=module, publication__status=Publication.STATUS['PUBLISHED']).count()
        else:
            count = 0

        shelf_html.append('<li class="shelf%s"><a href="%s">%s (%d)</a></li>' % (active_html, reverse(url, args=[shelf.id]), shelf.name, count))
    
    return ''.join(shelf_html)

# MODULES ################################################################################

@register.simple_tag
def print_publication_type_name(publication):
    return Module.objects.get(module_name=publication.publication_type).title

@register.simple_tag
def print_publication_title(publication, empty_string=''):
    title = publication.get_publication_title()
    if title:
        return publication.get_publication_title()
    else:
        return empty_string

class HasModuleNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, publisher, module_name):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.publisher = template.Variable(publisher)
        self.module_name = module_name.strip(' \"\'')
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        module_name = self.module_name
        
        if has_module(publisher=publisher, module=module_name):
            output = self.nodelist_true.render(context)
            return output
        else:
            output = self.nodelist_false.render(context)
            return output

@register.tag(name="has_module")
def do_has_module(parser, token):
    try:
        tag_name, publisher, module_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "has_module tag raise ValueError"
    
    nodelist_true = parser.parse(('else', 'end_has_module'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('end_has_module',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return HasModuleNode(nodelist_true, nodelist_false, publisher, module_name)

@register.simple_tag
def generate_publication_module_option_list(publisher):
    publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication')

    options = '<option></option>'
    for publisher_module in publisher_modules:
        options = options + '<option value="%s">%s</option>' % (publisher_module.module.module_name, publisher_module.module.title)
    
    return options

@register.simple_tag
def generate_publication_module_radio_list(publisher):
    publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication')

    radios = ''
    for publisher_module in publisher_modules:
        radios = radios + '<li><label><input type="radio" value="%s" name="module" /> <span>%s</span></label></li>' % (publisher_module.module.module_name, publisher_module.module.title)
    
    return radios

# Dashboard First-Time

class DashboardFirstTimeModalNode(template.Node):
    def __init__(self, publisher):
        self.publisher = template.Variable(publisher)
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication')

        dashboard_html = []
        for publisher_module in publisher_modules:
            try:
                t = loader.get_template('publisher/%s/snippets/dashboard_first_time_modal.html' % publisher_module.module.module_name)
                dashboard_html.append('<li>%s</li>' % t.render(context))
            except:
                pass
        
        if dashboard_html:
            return ''.join(dashboard_html)
        else:
            return u'<p>ยังไม่ติดตั้งโมดูล</p>'

@register.tag(name="generate_dashboard_first_time_modal")
def do_generate_dashboard_first_time_modal(parser, token):
    try:
        tag_name, publisher = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "generate_dashboard_first_time_modal tag raise ValueError"
    return DashboardFirstTimeModalNode(publisher)

class DashboardFirstTimeScriptNode(template.Node):
    def __init__(self, publisher):
        self.publisher = template.Variable(publisher)
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        publisher_modules = PublisherModule.objects.filter(publisher=publisher, module__module_type='publication')

        dashboard_html = []
        for publisher_module in publisher_modules:
            try:
                t = loader.get_template('publisher/%s/snippets/dashboard_first_time_script.html' % publisher_module.module.module_name)
                dashboard_html.append('%s' % t.render(context))
            except:
                pass
        
        return ''.join(dashboard_html)

@register.tag(name="generate_dashboard_first_time_script")
def do_generate_dashboard_first_time_script(parser, token):
    try:
        tag_name, publisher = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "generate_dashboard_first_time_script tag raise ValueError"
    return DashboardFirstTimeScriptNode(publisher)

# Publication Upload Modal

class PublicationModuleUploadModalNode(template.Node):
    def __init__(self, module_name):
        self.module_name = module_name.strip(' \"\'')
    
    def render(self, context):
        module_name = self.module_name

        if module_name:
            template_name = 'publisher/%s/snippets/upload_publication_modal.html' % module_name
        else:
            template_name = 'publisher/snippets/upload_publication_modal.html'

        try:
            t = loader.get_template(template_name)
            return t.render(context)
        except:
            return ''

@register.tag(name="generate_publication_module_upload_modal")
def do_generate_publication_module_upload_modal(parser, token):
    try:
        tag_name, module_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "publication_module_upload_modal tag raise ValueError"
    
    return PublicationModuleUploadModalNode(module_name)

# MANAGEMENT ################################################################################

@register.simple_tag
def print_publisher_status(publisher):
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