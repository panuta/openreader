import random
import re

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User, Permission
from django.db import models
from django.template.loader import render_to_string
from django.utils.hashcompat import sha_constructor

from common.permissions import can

"""
User Type
1. Reader [is_publisher=False]
   This user can only use an app on a device. Cannot login to website.

2. Publisher/Admin
   This user can do
      - Publisher management (Details, Users, Billing)
      - Publish permission
      - Publication management (Upload/Edit/Delete)
      - View all publisher's publication

3. Publisher/Staff
   This user can do
      - Publication management (Upload/Edit/Delete)
      - View all publisher's publication

4. Publisher/User
   This user can do
      - View all publisher's publication

"""

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class Role(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=200) # first_name and last_name in contrib.auth.User is too short
    last_name = models.CharField(max_length=200)
    is_publisher = models.BooleanField()
    is_first_time = models.BooleanField(default=True)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def can(self, action, object):
      return can(self.user, action, object)

    def get_fullname(self):
      return '%s %s' % (self.first_name, self.last_name)

# Publisher

class UserPublisher(models.Model):
    user = models.ForeignKey(User)
    publisher = models.ForeignKey('publisher.Publisher')
    role = models.ForeignKey(Role)
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.publisher.name)

class UserInvitationManager(models.Manager):

    def create_invitation(self, user_email, publisher, role, created_by):
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
        if isinstance(user_email, unicode):
            user_email = user_email.encode('utf-8')
        invitation_key = sha_constructor(salt+user_email).hexdigest()

        return self.create(user_email=user_email, publisher=publisher, role=role, invitation_key=invitation_key, created_by=created_by)
    
    def validate_invitation(self, invitation_key):
        if SHA1_RE.search(invitation_key):
            try:
                return self.get(invitation_key=invitation_key)
            except UserPublisherInvitation.DoesNotExist:
                return None
        else:
            return None
    
    def claim_invitation(self, invitation, user, is_default=False):
        user_publisher = UserPublisher.objects.create(user=user, publisher=invitation.publisher, role=invitation.role, is_default=is_default)
        invitation.delete()
        return user_publisher

class UserPublisherInvitation(models.Model):
    user_email = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.ForeignKey('publisher.Publisher')
    role = models.ForeignKey(Role)
    invitation_key = models.CharField(max_length=40, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_invitation_created_by')

    def __unicode__(self):
        return '%s:%s' % (self.user_email, self.publisher.name)

    objects = UserInvitationManager()

    def send_invitation_email(self):
        try:
            send_mail('%s want to invite you to join their team' % self.publisher.name, render_to_string('publisher/email_templates/user_publisher_invitation.html', {'invitation':self }), settings.EMAIL_FOR_USER_PUBLISHER_INVITATION, [self.user_email], fail_silently=False)
            return True
        except:
            return False

"""
class UserPublisherShelf(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey('publisher.PublisherShelf')
    can_manage = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_publisher_shelf_created_by')
"""

# Reader

class UserDevice(models.Model):
    user = models.ForeignKey(User)
    device_id = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.device_id)

class UserAccessToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=300)
    expired = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.token)

class UserPurchasedPublication(models.Model):
    user = models.ForeignKey(User)
    publication = models.ForeignKey('publisher.Publication')
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s:%s' % (self.user.get_profile().get_fullname(), self.publication.uid)

"""
# For fine-tuned permissions per user per publisher
class PublisherUserPermission(models.Model):
    publisher = models.ForeignKey('publisher.Publisher')
    user = models.ForeignKey(User)
    permissions = models.ManyToManyField(Permission, blank=True)
"""


