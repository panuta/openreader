from django.contrib import admin
from publisher.models import *

class PublisherAdmin(admin.ModelAdmin):
    pass

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_type')

class PublisherModuleAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'module', 'created')

class ReaderAppAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PublisherReaderAppAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'app', 'created')

class PublisherShelfAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'name', 'created')

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'uid')

class PublicationCategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(PublisherModule, PublisherModuleAdmin)
admin.site.register(ReaderApp, ReaderAppAdmin)
admin.site.register(PublisherReaderApp, PublisherReaderAppAdmin)
admin.site.register(PublisherShelf, PublisherShelfAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(PublicationCategory, PublicationCategoryAdmin)
