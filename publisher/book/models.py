from django.contrib.auth.models import User
from django.db import models

from publisher.models import Publication, PublicationCategory

class Book(models.Model):
    publication = models.OneToOneField(Publication)
    author = models.CharField(max_length=300)
    categories = models.ManyToManyField(PublicationCategory, related_name='book_categories', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
