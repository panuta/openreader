# -*- encoding: utf-8 -*-

import os, base64
import random

from datetime import date

from django.conf import settings
from dateutil import tz

from constants import THAI_MONTH_NAME, THAI_MONTH_ABBR_NAME

def format_full_datetime(datetime):
    try:
        localzone = tz.tzlocal()
        datetime = datetime.astimezone(localzone)
        return unicode('%d %s %d เวลา %02d:%02d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)
    except:
        return ''

def format_abbr_datetime(datetime):
    try:
        localzone = tz.tzlocal()
        datetime = datetime.astimezone(localzone)
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

def split_filepath(path):
    (head, tail) = os.path.split(path)
    (root, ext) = os.path.splitext(tail)

    if ext and ext[0] == '.':
        ext = ext[1:]
    
    return (head, root, ext)

def extract_parameters(parameters):
    param_list = parameters.split('&')
    parameters = {}
    for param in param_list:
        key, value = param.split('=')
        parameters[key] = value

    return parameters

def generate_random_username():
    return base64.urlsafe_b64encode(os.urandom(10))

RANDOM_STRING = 'qwertyuiopasdfghjklzxcvbnm1234567890'
def generate_random_string(string_length):
    str = []
    for i in range(0, string_length):
        str.append(random.choice(RANDOM_STRING))
    return ''.join(str)

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