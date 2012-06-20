from django.test import TestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

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
        
