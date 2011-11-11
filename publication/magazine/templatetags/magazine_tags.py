# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from publication.magazine.models import Magazine

@register.simple_tag
def generate_magazine_option_list(publisher):
    magazines = Magazine.objects.filter(publisher=publisher).order_by('title')

    options = '<option></option>'
    for magazine in magazines:
        options = options + '<option value="%d">%s</option>' % (magazine.id, magazine.title)
    
    return options

@register.simple_tag
def print_magazine_name(parent_id):
    try:
        magazine = Magazine.objects.get(id=parent_id)
        return magazine.title
    except Magazine.DoesNotExist:
        return ''