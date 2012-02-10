# -*- encoding: utf-8 -*-
import os, base64

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

def split_filename(filename):
    (name, ext) = os.path.splitext(filename)
    if ext and ext[0] == '.':
        ext = ext[1:]
    
    return (name, ext)

def generate_random_username():
    return base64.urlsafe_b64encode(os.urandom(10))

def humanize_file_size(size_in_byte):
    try:
        size_in_byte = int(size_in_byte)
        if size_in_byte > 1000000:
            return '%.2f เมกะไบต์' % (size_in_byte/1000000.0)
        elif size_in_byte > 1000:
            return '%.2f กิโลไบต์' % (size_in_byte/1000.0)
        else:
            return '%d ไบต์' % size_in_byte

    except:
        return u'ไม่สามารถหาขนาดได้'