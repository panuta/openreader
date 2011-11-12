# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse
from django.template import NodeList

from common.modules import *

from publication.models import PublisherModule

class HasModuleNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, publisher, module_name):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.publisher = template.Variable(publisher)
        self.module_name = module_name.strip(' \"\'')
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        module_name = self.module_name
        
        if has_module(publisher=publisher, module_name=module_name):
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
def generate_publication_menu(publisher):
    publication_types = PublisherModule.objects.filter(publisher=publisher, module_type='publication').order_by('created')

    menu_html = ''
    for publication_type in publication_types:
        module = __import__('publication.%s' % publication_type.module_name, fromlist=['publication'])
        menu_html = menu_html + '<li><a href="%s">%s</a></li>' % (reverse(module.FRONT_PAGE_URL_NAME, args=[publisher.id]), module.MODULE_NAME)
    
    return menu_html

@register.simple_tag
def generate_publication_module_option_list(publisher):
    modules = PublisherModule.objects.filter(publisher=publisher, module_type='publication')

    options = '<option></option>'
    for module in modules:
        module_object = module.get_module_object()
        options = options + '<option value="%s">%s</option>' % (module_object.MODULE_CODE, module_object.MODULE_NAME)
    
    return options

@register.simple_tag
def generate_publication_module_radio_list(publisher):
    modules = PublisherModule.objects.filter(publisher=publisher, module_type='publication')

    radios = ''
    for module in modules:
        module_object = module.get_module_object()
        radios = radios + '<li><label><input type="radio" value="%s" name="module" /> <span>%s</span></label></li>' % (module_object.MODULE_CODE, module_object.MODULE_NAME)
    
    return radios

class PublicationModuleUploadModalNode(template.Node):
    def __init__(self, module_name, publisher):
        self.module_name = module_name.strip(' \"\'')
        self.publisher = template.Variable(publisher)
    
    def render(self, context):
        publisher = self.publisher.resolve(context)
        module_name = self.module_name

        if module_name:
            template_name = 'publication/%s/snippets/upload_publication_modal.html' % module_name
        else:
            template_name = 'publication/snippets/upload_publication_modal.html'

        from django.template import loader
        try:
            t = loader.get_template(template_name)
            return t.render(context)
        except:
            return ''

@register.tag(name="generate_publication_module_upload_modal")
def do_generate_publication_module_upload_modal(parser, token):
    try:
        tag_name, module_name, publisher = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "publication_module_upload_modal tag raise ValueError"
    
    return PublicationModuleUploadModalNode(module_name, publisher)
