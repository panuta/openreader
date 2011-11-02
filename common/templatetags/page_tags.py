# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from common import utilities

# UPLOAD PUBLICATION #################################################################

@register.simple_tag
def print_upload_publication_legend(type):
    if type == 'periodical' or type == 'periodical-issue':
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

@register.simple_tag
def generate_upload_publication_modal(publisher, csrf_token):
    from django.core.urlresolvers import reverse

    return u"""<div class="modal hide fade" id="upload-publication-modal" style="display: none;">
            <form enctype="multipart/form-data" method="POST" action="%s" id="upload-publication-form">
                <div class="modal-header"><a class="close" href="#">×</a><h3>Upload publication</h3></div>
                <div class="modal-body">
                    <div style="display:none"><input type="hidden" value="%s" name="csrfmiddlewaretoken"></div>
                    <div class="inputs">
                        <div class="custom_inputs"></div>
                        <div class="periodical_inputs"><div class="clearfix"><label for="id_periodical">Periodical</label><div class="input"><select id="id_periodical" name="periodical">%s</select></div></div></div>
                        <div class="clearfix"><label for="id_publication">Publication file</label><div class="input"><input type="file" id="id_publication" name="publication"></div></div>
                        <input type="hidden" id="id_upload_type" name="upload_type" value=""/>
                        <input type="hidden" id="X-Progress-ID" name="X-Progress-ID" value=""/>
                    </div>
                </div>
                <div class="modal-footer"><input class="btn primary" type="submit" value="Upload" /></div>
            </form>
            </div>
            """ % (reverse('ajax_upload_publication', args=[publisher.id]), csrf_token, list_periodical(publisher))

