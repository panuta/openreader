"""
Module structure
- 'module_name' folder in publication app
- 'module_name' folder in templates
"""

from publisher.models import Module, PublisherModule

def get_publication_module(module_name, sub_module=''):
    try:
        module = Module.objects.get(module_name=module_name)
    except Module.DoesNotExist:
        return None
    return module.get_module_object(sub_module)

def has_module(publisher, module_name):
    return PublisherModule.objects.filter(publisher=publisher, module__module_name=module_name).exists()