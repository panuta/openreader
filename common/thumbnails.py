import subprocess, sys, traceback, os, logging
from PIL import Image

from django.conf import settings

from common.utilities import split_filepath

NO_THUMBNAIL_URL = settings.STATIC_URL + 'images/thumbnail_none.jpg'
PROCESSING_THUMBNAIL_URL = settings.STATIC_URL + 'images/thumbnail_processing.jpg'

logger = logging.getLogger(settings.OPENREADER_LOGGER)

def generate_thumbnails(publication):
    if publication.file_ext.lower() in ('jpg', 'jpeg', 'png', 'gif', 'psd'):
        return _generate_image_thumbnail(publication)
    elif publication.file_ext.lower() == 'pdf':
        return _generate_pdf_thumbnail(publication)
    elif publication.file_ext.lower() in ('mov', 'avi', 'mp4', 'flv', '3gp', 'ogg', 'webm', 'mpeg', 'm4v', 'mkv', 'wmv'):
        return _generate_video_thumbnail(publication)
    
    return False

def get_thumbnail_url(publication, size):
    if publication.has_thumbnail:
        return '%s%s/%s.%s.jpg' % (settings.THUMBNAIL_URL, publication.get_parent_folder(), publication.uid, size)
    else:
        if publication.is_processing:
            return PROCESSING_THUMBNAIL_URL
        else:
            return NO_THUMBNAIL_URL

def delete_thumbnails(publication):
    for thumbnail_size in settings.THUMBNAIL_SIZES:
        try:
            os.remove('%s%s/%s.%s.jpg' % (settings.THUMBNAIL_ROOT, publication.get_parent_folder(), publication.uid, thumbnail_size[0]))
        except:
            logger.error(traceback.format_exc(sys.exc_info()[2]))

# Thumbnail Generators
##############################################################################################################

def _generate_image_thumbnail(publication):
    try:
        im = Image.open(publication.uploaded_file.file)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.path)
        thumbnail_path = '%s%s/' % (settings.THUMBNAIL_ROOT, publication.get_parent_folder())

        if not os.path.exists(thumbnail_path):
            os.makedirs(thumbnail_path)
        
        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumb_im = im.copy()
            thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
            fullpath = '%s%s.%s.jpg' % (thumbnail_path, file_name, thumbnail_size[0])
            thumb_im.save(fullpath, 'JPEG')
        
        return True

    except:
        logger.error('Generating image thumbnail [%s] - %s' % (publication.uid, traceback.format_exc(sys.exc_info()[2])))
        return False

def _generate_base_thumbnail(publication, file_type, command='', callback=None):
    try:
        (file_path, file_name, file_ext) = split_filepath(publication.uploaded_file.path)

        temp_file = '%s%s.png' % (settings.THUMBNAIL_TEMP_ROOT, publication.uid)
        if not os.path.exists(settings.THUMBNAIL_TEMP_ROOT):
            os.makedirs(settings.THUMBNAIL_TEMP_ROOT)

        if command:
            command = command % (temp_file, publication.uploaded_file.path)
            command = command.split(' ')
            subprocess.call(command)

        if callback:
            callback(temp_file, publication.uploaded_file.path)

        im = Image.open(temp_file)
        if im.mode != 'RGB':
            im = im.convert('RGB')

        thumbnail_path = '%s%s/' % (settings.THUMBNAIL_ROOT, publication.get_parent_folder())

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
            logger.error(traceback.format_exc(sys.exc_info()[2]))

        return True

    except:
        logger.error('Generating %s thumbnail [%s] - %s' % (file_type, publication.uid, traceback.format_exc(sys.exc_info()[2])))
        return False

def _generate_pdf_thumbnail(publication):
    command = 'pdfdraw -r 100 -o %s %s 1'
    return _generate_base_thumbnail(publication, 'PDF', command=command)

def _generate_video_thumbnail(publication):

    def video_thumbnail(temp_file, uploaded_file):
        from ffvideo import VideoStream
        vs = VideoStream(uploaded_file)
        frame = vs.get_frame_at_sec(2)
        frame.image().save(temp_file)

    return _generate_base_thumbnail(publication, 'VIDEO', callback=video_thumbnail)

    
