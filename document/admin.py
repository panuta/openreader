from django.contrib import admin
from document.models import *

class OrganizationShelfAdmin(admin.ModelAdmin):
    pass

class OrganizationTagAdmin(admin.ModelAdmin):
    pass

class DocumentAdmin(admin.ModelAdmin):
    pass

class DocumentShelfAdmin(admin.ModelAdmin):
    pass

class DocumentTagAdmin(admin.ModelAdmin):
    pass

class ShelfPermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(OrganizationShelf, OrganizationShelfAdmin)
admin.site.register(OrganizationTag, OrganizationTagAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentShelf, DocumentShelfAdmin)
admin.site.register(DocumentTag, DocumentTagAdmin)
admin.site.register(ShelfPermission, ShelfPermissionAdmin)