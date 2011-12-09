from django.contrib import admin
from publisher.models import *

class CategoryAdmin(admin.ModelAdmin):
    pass

class MagazineAdmin(admin.ModelAdmin):
    pass

class MagazineIssueAdmin(admin.ModelAdmin):
    pass

class BookAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Magazine, MagazineAdmin)
admin.site.register(MagazineIssue, MagazineIssueAdmin)
admin.site.register(Book, BookAdmin)
