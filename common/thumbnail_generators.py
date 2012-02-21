import os
import subprocess
import Image

from django.conf import settings

from common.utilities import split_filepath

# Thumbnail Generator Classes
# - Thumbnails will be saved in ./thumbnails/
# - Thumbnail's name is [uid].thumbnail.[size].jpg

class BaseThumbnailGenerator(object):
    supported_file_type = []

    def generate_thumbnails(self, file):
        return False

class ImageThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['jpg', 'jpeg', 'png', 'gif']

    def generate_thumbnails(self, file):
        try:
            im = Image.open(file)
            if im.mode != 'RGB':
                im = im.convert('RGB')

            (path, filename) = os.path.split(file.name)
            filename = os.path.splitext(filename)[0]

            thumbnail_path = '%s/thumbnails/' % path

            if not os.path.exists(thumbnail_path):
                os.makedirs(thumbnail_path)
            
            for thumbnail_size in settings.THUMBNAIL_SIZES:
                thumb_im = im.copy()
                thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
                fullpath = '%s%s.thumbnail.%s.jpg' % (thumbnail_path, filename, thumbnail_size[0])
                thumb_im.save(fullpath, 'JPEG')
            
            return True

        except:
            return False

class PDFThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['pdf']
    
    def generate_thumbnails(self, file):
        try:
            (path, file_name, file_ext) = split_filepath(file.name)

            temp_file_path = '%s/%s.png' % (settings.THUMBNAIL_TEMP_ROOT, file_name)
            if not os.path.exists(settings.THUMBNAIL_TEMP_ROOT):
                os.makedirs(settings.THUMBNAIL_TEMP_ROOT)
            
            subprocess.call(['pdfdraw', '-r', '100', '-o', temp_file_path, file.name, '1'])

            im = Image.open(temp_file_path)
            if im.mode != 'RGB':
                im = im.convert('RGB')

            thumbnail_path = '%s/thumbnails/' % path

            if not os.path.exists(thumbnail_path):
                os.makedirs(thumbnail_path)
            
            for thumbnail_size in settings.THUMBNAIL_SIZES:
                thumb_im = im.copy()
                thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
                fullpath = '%s%s.thumbnail.%s.jpg' % (thumbnail_path, file_name, thumbnail_size[0])
                thumb_im.save(fullpath, 'JPEG')
            
            try:
                os.remove(temp_file_path)
            except:
                pass
            
            return True

        except:
            return False

class VideoThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['mp4']

    def generate_thumbnails(self, file):
        return False