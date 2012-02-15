import os

from django.conf import settings
from django.utils.importlib import import_module

from common.utilities import split_filename, split_filepath

NO_THUMBNAIL_URL = settings.STATIC_URL + 'images/no_thumbnail.jpg'

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

def get_thumbnail_url(publication, size):
    if publication.has_thumbnail:
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.name)
        return '%spublication/%d%s%s.thumbnail.%s.jpg' % (settings.MEDIA_URL, publication.organization.id, settings.THUMBNAIL_PATH, file_name, size)
    else:
        """
        if settings.THUMBNAIL_REGENERATE:
            (file_name, file_ext) = split_filename(publication.uploaded_file.name)
            generator = get_generator(file_ext)
            if generator:
                generated = generator.generate_thumbnails(publication.uploaded_file.file)
                publication.has_thumbnail = generated
                publication.save()
                return '%spublication/%d/thumbnails/%s.thumbnail.%s.jpg' % (settings.MEDIA_URL, publication.organization.id, file_name, size)
        """
                
        return NO_THUMBNAIL_URL

def delete_thumbnails(file): # file -> models.FieldFile
    (file_path, file_name, file_ext) = split_filepath(file.name)

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        try:
            os.remove('%s/%s%s.thumbnail.%s.jpg' % (file_path, settings.THUMBNAIL_PATH, file_name, thumbnail_size[0]))
        except:
            # TODO: Log error
            import sys
            print sys.exc_info()

