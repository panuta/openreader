# -*- encoding: utf-8 -*-

from django import template
register = template.Library()

from django.core.urlresolvers import reverse

from common import utilities

from accounts.models import UserPublisher

@register.simple_tag
def generate_publisher_menu(user):
    user_publishers = UserPublisher.objects.filter(user=user).order_by('publisher__name')

    if len(user_publishers) > 1:
        menus = []
        for user_publisher in user_publishers:
            menus.append('<li><a href="%s">%s</a></li>' % (reverse('view_publisher_dashboard', args=[user_publisher.publisher.id]), user_publisher.publisher.name))

        return '<ul class="nav secondary-nav"><li class="dropdown"><a class="dropdown-toggle" href="#">Switch Publisher</a><ul class="dropdown-menu">%s</ul></li></ul>' % ''.join(menus)
    else:
        return ''

