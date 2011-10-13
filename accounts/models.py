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

class UserBookLibrary(models.Model):
    user = models.ForeignKey(User)
    book = models.ForeignKey('publication.Book')
    created = models.DateTimeField(auto_now_add=True)

class UserPeriodicalIssueLibrary(models.Model):
    user = models.ForeignKey(User)
    issue = models.ForeignKey('publication.PeriodicalIssue')
    created = models.DateTimeField(auto_now_add=True)

