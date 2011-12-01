from django.contrib import admin
from publisher.book.models import *

class BookAdmin(admin.ModelAdmin):
    pass

admin.site.register(Book, BookAdmin)