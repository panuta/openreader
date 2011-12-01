import os
import Image

from django.conf import settings

class BaseThumbnailGenerator(object):
    supported_file_type = []

    def get_thumbnails(self, file):
        return None

class ImageThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['jpg', 'jpeg', 'png', 'gif']

    def get_thumbnails(self, file):
        (path, filename) = os.path.split(file.name)
        filename = os.path.splitext(filename)[0]
        im = Image.open(file)

        for thumbnail_size in settings.THUMBNAIL_SIZES:
            thumb_im = im.copy()
            thumb_im.thumbnail(thumbnail_size[1], Image.ANTIALIAS)
            fullpath = '%s/thumbnails/%s.thumbnail.%s.jpg' % (path, filename, thumbnail_size[0])
            thumb_im.save(fullpath, 'JPEG')
        
        return True

class PDFThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['pdf']

    def get_thumbnails(self, file):
        
        return None

class VideoThumbnailGenerator(BaseThumbnailGenerator):
    supported_file_type = ['mp4']

    def get_thumbnails(self, file):
        pass