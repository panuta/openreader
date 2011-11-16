# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from common import utilities

from accounts.models import UserPublisher
from publication.models import Publication

@register.simple_tag
def generate_publisher_menu(user):
    user_publishers = UserPublisher.objects.filter(user=user).order_by('publisher__name')

    if len(user_publishers) > 1:
        menus = []
        for user_publisher in user_publishers:
            menus.append('<li><a href="%s">Switch to %s</a></li>' % (reverse('view_publisher_dashboard', args=[user_publisher.publisher.id]), user_publisher.publisher.name))

        return u'<li class="dropdown"><a class="dropdown-toggle" href="#">เปลี่ยนสำนักพิมพ์</a><ul class="dropdown-menu">%s</ul></li>' % ''.join(menus)
    else:
        return ''

@register.simple_tag
def print_publication_status(publication):
    if publication.publish_status == Publication.PUBLISH_STATUS['UNPUBLISHED']:
        return '<span class="unpublished">Unpublished</span>'
    elif publication.publish_status == Publication.PUBLISH_STATUS['SCHEDULED']:
        return '<span class="scheduled">Scheduled to publish on %s by %s</span>' % (utilities.format_abbr_datetime(publication.publish_schedule), publication.published_by.get_profile().get_fullname())
    elif publication.publish_status == Publication.PUBLISH_STATUS['PUBLISHED']:
        return 'Published on <span>%s</span> by <span>%s</span>' % (utilities.format_abbr_datetime(publication.published), publication.published_by.get_profile().get_fullname())
    
    return ''

@register.simple_tag
def genetate_publication_category_multiple_checkbox(existing_categories):
    from publication.models import PublicationCategory

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
        htmls.append('<div class="span4"><ul>%s</ul></div>' % ''.join(columns[i]))
    
    return ''.join(htmls)
