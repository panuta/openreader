# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from publisher.magazine.models import Magazine

@register.simple_tag
def generate_magazine_option_list(publisher):
    magazines = Magazine.objects.filter(publisher=publisher).order_by('title')

    options = '<option></option>'
    for magazine in magazines:
        options = options + '<option value="%d">%s</option>' % (magazine.id, magazine.title)
    
    return options

@register.simple_tag
def generate_magazine_nav_list(publisher, active_magazine=None):
    magazines = Magazine.objects.filter(publisher=publisher).order_by('title')

    options = []
    for magazine in magazines:
        active_html = ' active' if active_magazine and magazine.id == active_magazine.id else ''
        options.append('<li class="publication%s"><a href="%s">%s</a></li>' % (active_html, reverse('view_magazine', args=[magazine.id]), magazine.title))
    
    return ''.join(options)

@register.simple_tag
def print_magazine_name(parent_id):
    try:
        magazine = Magazine.objects.get(id=parent_id)
        return magazine.title
    except Magazine.DoesNotExist:
        return ''