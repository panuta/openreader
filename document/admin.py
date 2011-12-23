from django.contrib import admin
from document.models import *

class OrganizationShelfAdmin(admin.ModelAdmin):
    pass

class DocumentAdmin(admin.ModelAdmin):
    pass

class DocumentShelfAdmin(admin.ModelAdmin):
    pass

class UserShelfPermissionAdmin(admin.ModelAdmin):
    pass

class UserInvitationShelfPermissionAdmin(admin.ModelAdmin):
    pass

admin.site.register(OrganizationShelf, OrganizationShelfAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentShelf, DocumentShelfAdmin)
admin.site.register(UserShelfPermission, UserShelfPermissionAdmin)
admin.site.register(UserInvitationShelfPermission, UserInvitationShelfPermissionAdmin)