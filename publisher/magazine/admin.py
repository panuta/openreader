from django.contrib import admin
from publisher.magazine.models import *

class MagazineAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'publisher')
    pass

class MagazineIssueAdmin(admin.ModelAdmin):
    pass

class MagazineIssueContentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Magazine, MagazineAdmin)
admin.site.register(MagazineIssue, MagazineIssueAdmin)
admin.site.register(MagazineIssueContent, MagazineIssueContentAdmin)