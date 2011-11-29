from django.contrib import admin
from publisher.models import *

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('module_name', 'module_type')

class ReaderAdmin(admin.ModelAdmin):
    list_display = ('name',)

class PublicationCategoryAdmin(admin.ModelAdmin):
    pass

class PublisherAdmin(admin.ModelAdmin):
    pass

class PublisherModuleAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'module', 'created')

class PublisherReaderAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'reader', 'created')

class PublisherShelfAdmin(admin.ModelAdmin):
    list_display = ('publisher', 'name', 'created')

class PublicationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'uid')

class PublicationShelfAdmin(admin.ModelAdmin):
    list_display = ('publication', 'shelf')

class PublicationReaderAdmin(admin.ModelAdmin):
    list_display = ('publication', 'reader')

admin.site.register(Module, ModuleAdmin)
admin.site.register(Reader, ReaderAdmin)
admin.site.register(PublicationCategory, PublicationCategoryAdmin)

admin.site.register(Publisher, PublisherAdmin)
admin.site.register(PublisherModule, PublisherModuleAdmin)
admin.site.register(PublisherReader, PublisherReaderAdmin)
admin.site.register(PublisherShelf, PublisherShelfAdmin)

admin.site.register(Publication, PublicationAdmin)
admin.site.register(PublicationShelf, PublicationShelfAdmin)
admin.site.register(PublicationReader, PublicationReaderAdmin)


