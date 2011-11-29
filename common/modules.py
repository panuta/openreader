"""
Module structure
- 'module_name' folder in publication app
- 'module_name' folder in templates
"""

def get_publication_module(module_name, sub_module=''):
    from publisher.models import Module

    try:
        module = Module.objects.get(module_name=module_name)
    except Module.DoesNotExist:
        return None
    return module.get_module_object(sub_module)

def has_module(publisher, module):
    from publisher.models import PublisherModule

    if isinstance(module, str) or isinstance(module, unicode):
        return PublisherModule.objects.filter(publisher=publisher, module__module_name=module).exists()
    else:
        return PublisherModule.objects.filter(publisher=publisher, module=module).exists()