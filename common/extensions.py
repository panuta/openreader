from django.conf import settings

def get_extension(class_name):
    try:
        extends = __import__('%s.extends' % (settings.SITE_TYPE), fromlist=[settings.SITE_TYPE])
        return getattr(extends, class_name)()
    except:
        return None

def get_extension_template(class_name, template_key, default=''):
    try:
        return get_extension(class_name).TEMPLATE_NAME[template_key]
    except:
        return default