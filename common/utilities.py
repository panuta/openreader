# -*- encoding: utf-8 -*-
import os

from datetime import date

from django.conf import settings

from constants import THAI_MONTH_NAME, THAI_MONTH_ABBR_NAME

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

def splitext(path):
    (file_name, file_ext) = os.path.splitext(path)
    if file_ext and file_ext[0] == '.':
        file_ext = file_ext[1:]
    
    return (file_name, file_ext)
