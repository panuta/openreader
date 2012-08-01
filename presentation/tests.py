from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.core.files import File
from domain.models import *
from signals import generate_publication_thumbnail

class GroupMemberTest(TestCase):
    fixtures = ['initial_data.json']

    def setUp(self):
        self.client.login(email='admin@openreader.com', password='1q2w3e4r')

    def tearDown(self):
        self.client.logout()

    def test_view_organization_group_member_404(self):
        response = self.client.get(reverse("view_organization_group_members", args=[999]))
        self.assertEqual(404, response.status_code)

    def test_view_organization_group_members(self):
        response = self.client.get(reverse("view_organization_group_members", args=[2])) # sale staff group
        self.assertEqual(200, response.status_code)
        
        # group is expected
        group = response.context["group"]
        self.assertFalse(group is None)
        self.assertEqual(u"Sale Staff", group.name)

        # group members is expected
        members = response.context["group_members"]
        self.assertFalse(members is None)
        self.assertEqual(1, members.count())
        self.assertEqual("staff@openreader.com", members[0].user_organization.user.email)

    def test_edit_user_from_view_organization_group_members(self):
        """
          Test redirct after edit group user
        """
        next = reverse('view_organization_group_members', args=[2])
        params = {
            'email': 'staff@openreader.com',
            'first_name': 'Staff',
            'last_name': 'OpenReader',
            'groups': [2],
            'admin_permissions': [],
            'next': next,
        }
        response = self.client.post(reverse("edit_organization_user", args=[2]), params, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertTrue(next in response.redirect_chain[0][0])
        
class SignalstTest(TestCase):

    def setUp(self):
        self.admin = User.objects.get(email='admin@openreader.com')
        self.opendream = Organization.objects.get(id=1)
        self.shelf = OrganizationShelf.objects.create(organization=self.opendream, name='Test Shelf', created_by=self.admin)
        self.pub = Publication(organization=self.opendream, title='Test Publication')
        self.pub.uploaded_file = File(open('README.md'))
        self.pub.uploaded_by = self.admin
        self.pub.save()
        PublicationShelf.objects.create(publication=self.pub, shelf=self.shelf, created_by=self.admin)

    def test_publication_uploaded_signal(self):
        generate_publication_thumbnail(sender=None, data=self.pub.id)
        self.assertTrue(True)
