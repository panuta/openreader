from django.contrib.auth.models import User, Permission
from django.db import models

"""
User Type
1. Reader [is_publisher=False]
   This user can only use an app on a device. Cannot login to website.

2. Publisher/Admin [is_publisher=True, is_admin=True]
   This user can do
      - Publisher management (Details, Users, Billing)
      - Publish permission
      - Publication management (Upload/Edit/Delete)
      - View all publication
    
    * Ignore UserPublisherShelf by letting this user access all shelf within its publisher

3. Publisher/Staff [is_publisher=True, is_admin=False, can_manage=True (UserPublisherShelf)]
   This user can do
      - Publication management (Upload/Edit/Delete) on permitted shelf
      - View permitted publication
    
    * Use UserPublisherShelf to determine user's permission on a specific shelf
    * If no UserPublisherShelf row for a specific shelf, then it will assume that the user doesn't have any permission

4. Publisher/User [is_publisher=True, is_admin=False, can_manage=False (UserPublisherShelf)]
   This user can do
      - View permitted publication

    * Use UserPublisherShelf to determine user's permission on a specific shelf

UserPublisherShelf
    - can_manage = True : User can Upload/Edit/Delete/Read
    - can_manage = False : User can Read
    - no row : User cannot do anything

"""

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=200, blank=True) # first_name and last_name in contrib.auth.User is too short
    last_name = models.CharField(max_length=200, blank=True)
    is_publisher = models.BooleanField()
    is_admin = models.BooleanField()

    def get_fullname(self):
      return '%s %s' % (self.first_name, self.last_name)

# Publisher

class UserPublisher(models.Model):
    user = models.ForeignKey(User)
    publisher = models.ForeignKey('publication.Publisher')
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class UserPublisherShelf(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey('publication.PublisherShelf')
    can_manage = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='user_publisher_shelf_created_by')

# Reader

class UserDevice(models.Model):
    user = models.ForeignKey(User)
    device_id = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)

class UserAccessToken(models.Model):
    user = models.ForeignKey(User)
    token = models.CharField(max_length=300)
    expired = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

class UserPurchasedPublication(models.Model):
    user = models.ForeignKey(User)
    publication = models.ForeignKey('publication.Publication')
    created = models.DateTimeField(auto_now_add=True)

"""
# For fine-tuned permissions per user per publisher
class PublisherUserPermission(models.Model):
    publisher = models.ForeignKey('publication.Publisher')
    user = models.ForeignKey(User)
    permissions = models.ManyToManyField(Permission, blank=True)
"""


