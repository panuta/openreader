import os
import subprocess
import Image

from django.conf import settings
from django.utils.importlib import import_module

from common.utilities import split_filepath

NO_THUMBNAIL_URL = settings.STATIC_URL + 'images/no_thumbnail.jpg'

def generate_thumbnails(publication):
    if publication.file_ext in ('jpg', 'jpeg', 'png', 'gif'):
        return _generate_image_thumbnail(publication)
    elif publication.file_ext == 'pdf':
        return _generate_pdf_thumbnail(publication)
    
    return False

def get_thumbnail_url(publication, size):
    if publication.has_thumbnail:
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.name)
        return '%s%s%s/%s.%s.jpg' % (settings.MEDIA_URL, publication.get_rel_path(), settings.THUMBNAIL_PREFIX_PATH, publication.uid, size)
    else:
        return NO_THUMBNAIL_URL

def delete_thumbnails(publication):
    (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.path)

    for thumbnail_size in settings.THUMBNAIL_SIZES:
        try:
            os.remove('%s%s/%s.%s.jpg' % (file_path, settings.THUMBNAIL_PREFIX_PATH, file_name, thumbnail_size[0]))
        except:
            # TODO LOG
            pass

# Thumbnail Generators
##############################################################################################################

def _generate_image_thumbnail(publication):
    try:
        im = Image.open(publication.uploaded_file.file)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.path)
        thumbnail_path = '%s%s/' % (file_path, settings.THUMBNAIL_PREFIX_PATH)

        if not os.path.exists(thumbnail_path):
            os.makedirs(thumbnail_path)
        
        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumb_im = im.copy()
            thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
            fullpath = '%s%s.%s.jpg' % (thumbnail_path, file_name, thumbnail_size[0])
            thumb_im.save(fullpath, 'JPEG')
        
        return True

    except:
        # TODO LOG
        return False

def _generate_pdf_thumbnail(publication):
    try:
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.path)

        temp_file = '%s%s.png' % (settings.THUMBNAIL_TEMP_ROOT, publication.uid)
        if not os.path.exists(settings.THUMBNAIL_TEMP_ROOT):
            os.makedirs(settings.THUMBNAIL_TEMP_ROOT)
        
        subprocess.call(['pdfdraw', '-r', '100', '-o', temp_file, publication.uploaded_file.path, '1'])

        im = Image.open(temp_file)
        if im.mode != 'RGB':
            im = im.convert('RGB')

        thumbnail_path = '%s%s/' % (file_path, settings.THUMBNAIL_PREFIX_PATH)

        if not os.path.exists(thumbnail_path):
            os.makedirs(thumbnail_path)
        
        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumb_im = im.copy()
            thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
            fullpath = '%s%s.%s.jpg' % (thumbnail_path, file_name, thumbnail_size[0])
            thumb_im.save(fullpath, 'JPEG')
        
        try:
            os.remove(temp_file)
        except:
            pass
        
        return True

    except:
        return False

"""
def get_thumbnail_url(publication, size):
    if publication.has_thumbnail:
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.name)
        return '%spublication/%d%s%s.thumbnail.%s.jpg' % (settings.MEDIA_URL, publication.organization.id, settings.THUMBNAIL_PATH, file_name, size)
    else:
        #if settings.THUMBNAIL_REGENERATE:
        #    (file_name, file_ext) = split_filename(publication.uploaded_file.name)
        #    generator = get_generator(file_ext)
        #    if generator:
        #        generated = generator.generate_thumbnails(publication.uploaded_file.file)
        #        publication.has_thumbnail = generated
        #        publication.save()
        #        return '%spublication/%d/thumbnails/%s.thumbnail.%s.jpg' % (settings.MEDIA_URL, publication.organization.id, file_name, size)
        
        return NO_THUMBNAIL_URL

"""