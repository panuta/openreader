from django.contrib import admin
from publisher.book.models import *

class BookAdmin(admin.ModelAdmin):
    pass

class BookContentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Book, BookAdmin)
admin.site.register(BookContent, BookContentAdmin)