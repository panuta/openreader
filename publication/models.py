import uuid

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models

from private_files import PrivateFileField

def is_downloadable(request, instance):
    return True

def publication_media_dir(instance, filename):
    return '%s%s/%s' % (settings.PUBLICATION_ROOT, instance.publisher.id, filename)

class Publisher(models.Model):
    name = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='publisher_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publisher_modified_by')

class UploadingPublication(models.Model):
    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    publication_type = models.CharField(max_length=50)

    uploaded_file = models.FileField(upload_to=publication_media_dir, max_length=500)

    file_name = models.CharField(max_length=200)
    file_ext = models.CharField(max_length=10)

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='uploading_publication_uploaded_by')

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(UploadingPublication, self).save(*args, **kwargs)

class Publication(models.Model):
    PUBLISH_STATUS_UNPUBLISHED = 1
    PUBLISH_STATUS_READY_TO_PUBLISH = 2
    PUBLISH_STATUS_PUBLISHED = 3
    PUBLISH_STATUS_SCHEDULE_TO_PUBLISH = 4

    publisher = models.ForeignKey('Publisher')

    uid = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50)

    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable, max_length=500)
    file_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)

    publish_status = models.IntegerField(default=PUBLISH_STATUS_UNPUBLISHED)
    publish_schedule = models.DateTimeField(null=True)
    published = models.DateTimeField(null=True, auto_now_add=True)
    published_by = models.ForeignKey(User, null=True, related_name='publication_published_by')

    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, related_name='publication_uploaded_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='publication_modified_by')

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super(Publication, self).save(*args, **kwargs)

class PublicationCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

# Publication - Book ############################################################

class Book(models.Model):
    publication = models.ForeignKey('Publication')
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    categories = models.ManyToManyField('PublicationCategory', related_name='book_categories')

class BookContent(models.Model):
    book = models.ForeignKey('Book')
    title = models.CharField(max_length=255)
    start_page = models.IntegerField()

# Publication - Periodical ############################################################

class Periodical(models.Model):
    publisher = models.ForeignKey('Publisher')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField('PublicationCategory', related_name='periodical_categories')

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='periodical_created_by')
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='periodical_modified_by')

class PeriodicalIssue(models.Model):
    publication = models.ForeignKey('Publication')
    periodical = models.ForeignKey('Periodical')

class PeriodicalIssueContent(models.Model):
    issue = models.ForeignKey('PeriodicalIssue')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    start_page = models.IntegerField()


"""
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models

from private_files import PrivateFileField

#from djangotoolbox.fields import EmbeddedModelField, ListField

from common.models import Loggable


PUBLICATION_TYPES = (
    (1, 'Book'),
    (2, 'Periodical')
)

PUBLICATION_STATUSES = (
    (1, 'Draft'),
    (2, 'Pending'),
    (3, 'Published'),
    (4, 'Unpublished')
)

PERIODICAL_TYPES = (
    (1, 'Magazine'),
)


# Manager ---------------------------------------------------------------------

class PublicationManager:
    def topic_of_contents(self, kwargs=None):
        if kwargs:
            if 'page' in kwargs and 'title' in kwargs:
                return TopicOfContents.objects.get(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            page=kwargs['page'],
                            title=kwargs['title'])
            elif 'page' in kwargs:
                return TopicOfContents.objects.filter(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            page=kwargs['page'])
            elif 'title' in kwargs:
                return TopicOfContents.objects.filter(
                            publication_type=self.TYPE,
                            publication_id=self.id,
                            title=kwargs['title'])
            else:
                return []
        else:
            return TopicOfContents.objects.filter(
                        publication_type=self.TYPE,
                        publication_id=self.id)

    def file_url(self):
        try:
            f = FileUpload.objects.get(publication_type=self.TYPE, publication_id=self.id)
            return f.uploaded_file.url
        except:
            return ''

    def thumbnail_pages(self):
        return [1, 2, 3] # TODO: generate thumbnail of pages

    def instance_of(self):
        return self.__class__.__name__

    def total_downloads(self):
        from statistic.models import CountedFileDownloadsManager # fix circular imports
        return CountedFileDownloadsManager(obj=self).total_downloads()

    def last_week_downloads(self):
        from statistic.models import CountedFileDownloadsManager # fix circular imports
        return CountedFileDownloadsManager(obj=self).last_week_downloads()

    def last_month_downloads(self):
        from statistic.models import CountedFileDownloadsManager # fix circular imports
        return CountedFileDownloadsManager(obj=self).last_month_downloads()

# Callback Methods ------------------------------------------------------------

def is_downloadable(request, instance):
    return True # TODO: implement

def publication_media_dir(instance, filename):
    return '/'.join([settings.PUBLICATION_DIR, filename])


# DB Models -------------------------------------------------------------------

class Publisher(Loggable):
    owner = models.ForeignKey(User, related_name='owner')
    collaborators = models.ManyToManyField(User, related_name='collaborators')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)

    def draft_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_DRAFT)

    def pending_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_PENDING)

    def published_issues(self):
        periodicals = self.periodical_set.all().values('pk')
        return Issue.objects.filter(periodical__in=periodicals,
                                    status=Publication.STATUS_PUBLISHED)


class Publication(Loggable):
    publisher = models.ForeignKey('Publisher')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    BOOK = 1
    PERIODICAL = 2

    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_PUBLISHED = 3
    STATUS_UNPUBLISHED = 4

    def save_categories(self, post_vars):
        categories = []
        for key in post_vars:
            if key.find('category_') == 0:
                pk = key.split('_')[1]
                categories.append(Category.objects.get(pk=pk))
        self.categories = categories
        self.save()

    class Meta:
        abstract = True


class Book(Publication, PublicationManager):
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    status = models.IntegerField(choices=PUBLICATION_STATUSES, default=1, db_index=True)
    pending_until = models.DateTimeField(null=True, blank=True)
    categories = models.ManyToManyField('Category', related_name='book_categories')

    TYPE = Publication.BOOK


class Periodical(Publication):
    periodical_type = models.IntegerField(choices=PERIODICAL_TYPES, default=1, db_index=True)
    categories = models.ManyToManyField('Category', related_name='periodical_categories')


class Issue(Loggable, PublicationManager):
    periodical = models.ForeignKey('Periodical')
    issued_at = models.DateField()
    description = models.TextField(null=True, blank=True)
    status = models.IntegerField(choices=PUBLICATION_STATUSES, default=1, db_index=True)
    pending_until = models.DateTimeField(null=True, blank=True)

    TYPE = Publication.PERIODICAL

    class Meta:
        get_latest_by = 'created_at'


class FileUpload(Loggable):
    uploader = models.ForeignKey(User)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    publication_id = models.CharField(max_length=10, db_index=True)
    uploaded_file = PrivateFileField(upload_to=publication_media_dir, condition=is_downloadable)


class TopicOfContents(Loggable):
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, db_index=True)
    publication_id = models.CharField(max_length=10, db_index=True)
    page = models.CharField(max_length=3)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100, null=True, blank=True)


class Category(Loggable):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)


class PublisherUserPermission(Loggable):
    publisher = models.ForeignKey(Publisher)
    user = models.ForeignKey(User)
    permission = models.ForeignKey(Permission)

    class Meta:
        db_table = 'publication_publisher_user_permissions'


# MongoDB ---------------------------------------------------------------------

#class TopicOfContents(models.Model):
#    page = models.CharField(max_length=3)
#    title = models.CharField(max_length=255)
#    author = models.CharField(max_length=100)
#
#
#class BookMetadata(models.Model):
#    book_id = models.CharField(max_length=10)
#    toc = ListField(EmbeddedModelField('TopicOfContents'))
#
#
#class IssueMetadata(models.Model):
#    issue_id = models.CharField(max_length=10)
#    toc = ListField(EmbeddedModelField('TopicOfContents'))

"""