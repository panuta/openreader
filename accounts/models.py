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
    
    * Ignore UserShelfPermission by letting this user access all shelf within its publisher

3. Publisher/Staff [is_publisher=True, is_admin=False, is_staff=True (UserPublisherShelf)]
   This user can do
      - Publication management (Upload/Edit/Delete) on permitted shelf
      - View permitted publication
    
    * Use UserShelfPermission to determine user's permission on a specific shelf
    * If no UserShelfPermission row for a specific shelf, then it will assume that the user doesn't have any permission

4. Publisher/User [is_publisher=True, is_admin=False, is_staff=False (UserPublisherShelf)]
   This user can do
      - View permitted publication

    * Use UserShelfPermission to determine user's permission on a specific shelf

UserShelfPermission
    - is_staff = True : User can Upload/Edit/Delete/Read
    - is_staff = False : User can Read
    - no row : User cannot do anything

"""

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_publisher = models.BooleanField()
    is_admin = models.BooleanField()

class UserPublisher(models.Model):
    user = models.ForeignKey(User)
    publisher = models.ForeignKey('publication.Publisher')
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class UserPublisherShelf(models.Model):
    user = models.ForeignKey(User)
    shelf = models.ForeignKey('publication.PublisherShelf')
    is_staff = models.BooleanField()

"""
# For finer-tuned permissions per user per publisher
class PublisherUserPermission(models.Model):
    publisher = models.ForeignKey('publication.Publisher')
    user = models.ForeignKey(User)
    permissions = models.ManyToManyField(Permission, blank=True)
"""

class UserPurchasedPublication(models.Model):
    user = models.ForeignKey(User)
    publication = models.ForeignKey('publication.Publication')
    created = models.DateTimeField(auto_now_add=True)
