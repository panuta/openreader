# -*- encoding: utf-8 -*-

from datetime import date, time

from django.conf import settings
from django.forms.util import flatatt
from django.forms.widgets import Input, TimeInput
from django.utils import datetime_safe
from django.utils.dateformat import format
from django.utils.safestring import mark_safe

class YUICalendar(Input):
    input_type = 'text'
    format = '%Y-%m-%d'

    def __init__(self, attrs=None):
        self.attrs = attrs
	
    def _format_value(self, value):
        if value is None:
            return ''
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_date(value)
            return value.strftime(self.format)
        return value
    
    def render(self, name, value, attrs=None):
        input_id = self.attrs.get('id', 'date_picker') if self.attrs else 'date_picker'
        
        if not value:
            display_value = ''
            value = ''
        else:
            if type(value).__name__ == 'unicode':
                (year, month, day) = value.split('-')
                value = date(int(year), int(month), int(day))
            
            display_value = '%s %s' % (format(value, 'j F'), (value.year+543))
            value = '%d-%d-%d' % (value.year, value.month, value.day)
        
        value_input = '<input type="hidden" name="%s" value="%s" id="%s_value"/>' % (name, value, input_id)
        display_input = '<input type="text" value="%s" id="%s_display" class="yui_date_picker_textbox"/>' % (display_value, input_id)
        calendar_icon = '<button id="%s" class="yui_date_picker">Select date</button>' % (input_id)
        
        return mark_safe(u'<span class="yui_date_picker_panel">%s%s%s</span>' % (calendar_icon, value_input, display_input))
    
    def _has_changed(self, initial, data):
        return super(YUICalendar, self)._has_changed(self._format_value(initial), data)
    
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'libs/yui/build/container/assets/skins/sam/container.css',
                settings.STATIC_URL + 'libs/yui/build/calendar/assets/skins/sam/calendar.css',
                settings.STATIC_URL + 'css/yui.calendar.widget.css',
            ),
        }
        js = (
            settings.STATIC_URL + 'libs/yui/build/yahoo-dom-event/yahoo-dom-event.js',
            settings.STATIC_URL + 'libs/yui/build/element/element-min.js',
            settings.STATIC_URL + 'libs/yui/build/container/container-min.js',
            settings.STATIC_URL + 'libs/yui/build/calendar/calendar-min.js',
            settings.STATIC_URL + 'js/yui.calendar.widget.js',
        )

class HourMinuteTimeInput(TimeInput):
    format = '%H:%M'

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        input_id = final_attrs.get('id')

        if not value:
            hour_value = None
            minute_value = None
        elif isinstance(value, time):
            hour_value = int(value.hour)
            minute_value = int(value.minute)
        else:
            (hour_value, minute_value) = value.split(':')
            hour_value = int(hour_value)
            minute_value = int(minute_value)
        
        hour_options = ['<option></option>']
        for hour in range(0, 24):
            selected_html = (hour == hour_value) and u' selected="selected"' or ''
            hour_options.append('<option value="%d"%s>%02d</option>' % (hour, selected_html, hour))
        
        minute_options = ['<option></option>']
        for minute in range(0, 60, 15):
            selected_html = (minute == minute_value) and u' selected="selected"' or ''
            minute_options.append('<option value="%d"%s>%02d</option>' % (minute, selected_html, minute))

        return mark_safe(u'<select name="%s_hour" id="%s_hour">%s</select>:<select name="%s_minute" id="%s_minute">%s</select> น.' % (name, input_id, ''.join(hour_options), name, input_id, ''.join(minute_options)))
    
    def value_from_datadict(self, data, files, name):
        return '%s:%s' % (data.get(name + '_hour'), data.get(name + '_minute')) if data.get(name + '_hour') and data.get(name + '_minute') else ''
    
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'css/hour_only_time.widget.css',
            ),
        }

class HourOnlyTimeInput(TimeInput):
    format = '%H:%M'

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        input_id = self.attrs.get('id', 'hour_time') if self.attrs else 'hour_time'

        if not value:
            value = None
        else:
            value = int(value.split(':')[0])

        options = '<option></option>'
        for hour in range(0, 24):
            if hour == value:
                options = options + '<option value="%d:00" selected="selected">%02d</option>' % (hour, hour)
            else:
                options = options + '<option value="%d:00">%02d</option>' % (hour, hour)

        return mark_safe(u'<div class="widget_hour_only_time">เวลา <select name="%s" id="%s">%s</select>:00 น.</div>' % (name, input_id, options))
    
    class Media:
        css = {
            'all': (
                settings.STATIC_URL + 'css/hour_only_time.widget.css',
            ),
        }


"""
class HourOnlyTime(Input):
    input_type = 'text'
    format = '%H'

    def _format_value(self, value):
        if value is None:
            return ''
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_date(value)
            return value.strftime(self.format)
        return value
    
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)



        input_id = self.attrs.get('id', 'hour_time') if self.attrs else 'hour_time'
        
        if not value:
            value = ''
        else:
            value = str(value)

        value_input = '' % ()
        display_input = '<span id="%s_display" class="yui_date_picker_textbox">%s</span>' % (input_id, display_value)
        calendar_icon = '<img src="%s/images/input/date_picker.png" id="%s" class="yui_date_picker"/>' % (settings.STATIC_URL, input_id)
        
        return mark_safe(u'<span class="widget_hour_only_time"><input type="text" name="%s" value="%s" id="%s"/>:00</span>' % (name, value, input_id, ))

"""

