from django.db import models

from publication.models import Publication, PublicationCategory

class Book(models.Model):
    publication = models.OneToOneField(Publication)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    categories = models.ManyToManyField(PublicationCategory, related_name='book_categories', null=True)

class BookContent(models.Model):
    book = models.ForeignKey('Book')
    title = models.CharField(max_length=255)
    start_page = models.IntegerField()