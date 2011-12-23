from django.contrib import admin
from accounts.models import *

class RoleAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.ModelAdmin):
    pass

class OrganizationAdmin(admin.ModelAdmin):
    pass

class UserOrganizationAdmin(admin.ModelAdmin):
    pass

class UserOrganizationInvitationAdmin(admin.ModelAdmin):
    pass

class UserDeviceAdmin(admin.ModelAdmin):
    pass

class UserAccessTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(Role, RoleAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(UserOrganization, UserOrganizationAdmin)
admin.site.register(UserOrganizationInvitation, UserOrganizationInvitationAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(UserAccessToken, UserAccessTokenAdmin)