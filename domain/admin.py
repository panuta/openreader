from django.contrib import admin

from domain.models import *

# USER ACCOUNT #########################################################################################################

class OrganizationAdmin(admin.ModelAdmin):
    pass

class OrganizationGroupAdmin(admin.ModelAdmin):
    pass

class UserOrganizationAdmin(admin.ModelAdmin):
    pass

class UserGroupAdmin(admin.ModelAdmin):
    pass

class UserOrganizationInvitationAdmin(admin.ModelAdmin):
    pass

class UserOrganizationInvitationUserGroupAdmin(admin.ModelAdmin):
    pass

#admin.site.register(Organization, OrganizationAdmin)
#admin.site.register(OrganizationGroup, OrganizationGroupAdmin)
#admin.site.register(UserOrganization, UserOrganizationAdmin)
#admin.site.register(UserGroup, UserGroupAdmin)
#admin.site.register(UserOrganizationInvitation, UserOrganizationInvitationAdmin)
#admin.site.register(UserOrganizationInvitationUserGroup, UserOrganizationInvitationUserGroupAdmin)

# DOCUMENT #############################################################################################################

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

class OrganizationDownloadServerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Publication, PublicationAdmin)
admin.site.register(OrganizationShelf, OrganizationShelfAdmin)
admin.site.register(PublicationShelf, PublicationShelfAdmin)
admin.site.register(OrganizationShelfPermission, OrganizationShelfPermissionAdmin)
admin.site.register(GroupShelfPermission, GroupShelfPermissionAdmin)
admin.site.register(UserShelfPermission, UserShelfPermissionAdmin)
admin.site.register(OrganizationTag, OrganizationTagAdmin)
admin.site.register(PublicationTag, PublicationTagAdmin)
admin.site.register(OrganizationDownloadServer, OrganizationDownloadServerAdmin)
