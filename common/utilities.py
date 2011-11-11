# -*- encoding: utf-8 -*-

from datetime import date

from django.conf import settings

from constants import THAI_MONTH_NAME, THAI_MONTH_ABBR_NAME

from publication.models import Publication

def format_full_datetime(datetime):
    try:
        return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)
    except:
        return ''

def format_abbr_datetime(datetime):
    try:
        return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)
    except:
        return ''

def format_full_date(datetime):
    try:
        return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543)
    except:
        return ''

def format_abbr_date(datetime):
    try:
        return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543)
    except:
        return ''

# PUBLICATION

def convert_publish_status(status_string):
    if status_string == 'unpublished':
        return Publication.PUBLISH_STATUS_UNPUBLISHED
    elif status_string == 'ready':
        return Publication.PUBLISH_STATUS_READY_TO_PUBLISH
    elif status_string == 'scheduled':
        return Publication.PUBLISH_STATUS_SCHEDULE_TO_PUBLISH
    elif status_string == 'published':
        return Publication.PUBLISH_STATUS_PUBLISHED
    else:
        return 0

def convert_publication_type(type_string):
    if type_string == 'book':
        return Publication.PUBLICATION_TYPE_BOOK
    elif type_string == 'magazine':
        return Publication.PUBLICATION_TYPE_MAGAZINE
    else:
        return 0