from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    is_publisher = models.BooleanField(default=False)

class UserPublisher(models.Model):
    user = models.ForeignKey(User)
    publisher = models.ForeignKey('publication.Publisher')
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class UserPurchasedPublication(models.Model):
    user = models.ForeignKey(User)
    publication = models.ForeignKey('Publication')
    created = models.DateTimeField(auto_now_add=True)
