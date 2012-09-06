"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import base64

from django.test import TestCase
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.core.files import File
from django.contrib.auth.models import User
from domain.models import *

from StringIO import StringIO

class APITest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        credentials = base64.b64encode('admin@openreader.com:1q2w3e4r')
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials

        self.admin = User.objects.get(email='admin@openreader.com')
        self.opendream = Organization.objects.get(id=1)
        self.shelf = OrganizationShelf.objects.create(organization=self.opendream, name='Test Shelf', created_by=self.admin)
        self.shelf2 = OrganizationShelf.objects.create(organization=self.opendream, name='Test Shelf 2', created_by=self.admin)
        self.pub = Publication(organization=self.opendream, title='Test Publication')
        self.pub.uploaded_file = File(open('README.md'))
        self.pub.uploaded_by = self.admin
        self.pub.save()
        PublicationShelf.objects.create(publication=self.pub, shelf=self.shelf, created_by=self.admin)


    def tearDown(self):
        self.client.logout()

    def test_list_publication(self):
        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        self.assertTrue(json_data['organization'])
        self.assertEquals('Opendream', json_data['organization']['name'])
        self.assertEquals(2, len(json_data['shelves']))

    def test_admin_shelf_archive(self):
        self.shelf.archive = True
        self.shelf.save()

        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        self.assertTrue(json_data['shelves'][0]['archive'])

        self.shelf.archive = False
        self.shelf.save()

        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        self.assertFalse(json_data['shelves'][0]['archive'])

        UserShelfArchive.objects.create(shelf=self.shelf, user=self.admin)

        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        self.assertTrue(json_data['shelves'][0]['archive'])

    def test_user_archive_shelves(self):
        shelves = '%s|%s' % (self.shelf.id, self.shelf2.id)

        response = self.client.get(reverse('api_user_config_shelves'), {'archive_shelves': shelves})
        self.assertEquals(200, response.status_code)

        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        
        for s in json_data['shelves']:
            self.assertTrue(s['archive'])

        response = self.client.get(reverse('api_user_config_shelves'), {'unarchive_shelves': shelves})
        self.assertEquals(200, response.status_code)

        response = self.client.get(reverse('api_list_publication'), {'organization': 'opendream'})
        json_data = simplejson.load(StringIO(response.content))
        
        for s in json_data['shelves']:
            self.assertFalse(s['archive'])

    def test_list_user_organization(self):
        # admin@openreader.com has 2 organizations
        response = self.client.get(reverse('api_list_user_organization'))
        json_data = simplejson.load(StringIO(response.content))
        self.assertEquals(2, len(json_data['organizations']))
        self.assertTrue(json_data['user_profile'])
        self.assertEquals(json_data['user_profile']['first_name'], 'Admin')

        # staff@openreader.com has 1 organization
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic %s' % base64.b64encode('staff@openreader.com:1q2w3e4r')
        response = self.client.get(reverse('api_list_user_organization'))
        json_data = simplejson.load(StringIO(response.content))
        self.assertEquals(1, len(json_data['organizations']))

        # system@openreader.com has no organization
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Basic %s' % base64.b64encode('system@openreader.com:1q2w3e4r')
        response = self.client.get(reverse('api_list_user_organization'))
        json_data = simplejson.load(StringIO(response.content))
        self.assertEquals(0, len(json_data['organizations']))


    def test_request_download_publication(self):
        response = self.client.get(reverse('api_request_download_publication', args=[self.pub.uid]))
        self.assertEquals(200, response.status_code)
