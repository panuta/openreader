from django.contrib import admin
from document.models import *

class PublicationAdmin(admin.ModelAdmin):
    pass

class OrganizationShelfAdmin(admin.ModelAdmin):
    pass

class PublicationShelfAdmin(admin.ModelAdmin):
    pass

class OrganizationShelfPermissionAdmin(admin.ModelAdmin):
    pass

class GroupShelfPermissionAdmin(admin.ModelAdmin):
    pass

class UserShelfPermissionAdmin(admin.ModelAdmin):
    pass

class OrganizationTagAdmin(admin.ModelAdmin):
    pass

class PublicationTagAdmin(admin.ModelAdmin):
    pass

admin.site.register(Publication, PublicationAdmin)
admin.site.register(OrganizationShelf, OrganizationShelfAdmin)
admin.site.register(PublicationShelf, PublicationShelfAdmin)
admin.site.register(OrganizationShelfPermission, OrganizationShelfPermissionAdmin)
admin.site.register(GroupShelfPermission, GroupShelfPermissionAdmin)
admin.site.register(UserShelfPermission, UserShelfPermissionAdmin)
admin.site.register(OrganizationTag, OrganizationTagAdmin)
admin.site.register(PublicationTag, PublicationTagAdmin)