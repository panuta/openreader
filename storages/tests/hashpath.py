import os
import shutil

from django.test import TestCase
from django.core.files.base import ContentFile
from django.conf import settings

from storages.backends.hashpath import HashPathStorage


class HashPathStorageTest(TestCase):

    def setUp(self):
        self.storage = HashPathStorage()
        
        # make sure the profile upload folder exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
            
    def tearDown(self):
        # remove uploaded profile picture
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_save_same_file(self):
        """
        saves a file twice, the file should only be stored once, because the
        content/hash is the same
        """
        
        path_1 = self.storage.save('test', ContentFile('new content'))
        
        path_2 = self.storage.save('test', ContentFile('new content'))

        self.assertEqual(path_1, path_2)
