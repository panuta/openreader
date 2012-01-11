from django.contrib import admin
from accounts.models import *

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


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationGroup, OrganizationGroupAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(UserOrganizationInvitation, UserOrganizationInvitationAdmin)
admin.site.register(UserOrganizationInvitationUserGroup, UserOrganizationInvitationUserGroupAdmin)