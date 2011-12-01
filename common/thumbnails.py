from django.conf import settings
from django.utils.importlib import import_module

def load_generator(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]

    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing thumbnail generator %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing thumbnail generator. Is THUMBNAIL_GENERATORS a correctly defined list or tuple?')
    
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" thumbnail generator' % (module, attr))
    
    return cls()

def get_generator(file_type):
    generators = settings.THUMBNAIL_GENERATORS

    for generator_name in generators:
        generator = load_generator(generator_name)

        if file_type in generator.supported_file_type:
            return generator
    
    return None

