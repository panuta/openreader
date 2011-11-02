# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from common import utilities

# UPLOAD PUBLICATION #################################################################

@register.simple_tag
def print_upload_publication_legend(type):
    if type == 'periodical':
        return 'Upload periodical issue'
    elif type == 'book':
        return 'Upload book'
    
    return 'Upload publication'

@register.simple_tag
def list_periodical(publisher):
    from publication.models import Periodical
    periodicals = Periodical.objects.filter(publisher=publisher).order_by('title')

    options = '<option></option>'
    for periodical in periodicals:
        options = options + '<option value="%s">%s</option>' % (periodical.id, periodical.title)

    return options

@register.simple_tag
def print_periodical_name(parent_id):
    from publication.models import Periodical

    try:
        periodical = Periodical.objects.get(id=parent_id)
        return periodical.title
    except Periodical.DoesNotExist:
        return ''



