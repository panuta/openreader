from django.contrib import admin
from accounts.models import *

class RoleAdmin(admin.ModelAdmin):
    pass

class UserProfileAdmin(admin.ModelAdmin):
    pass

class UserPublisherAdmin(admin.ModelAdmin):
    pass

class UserPublisherInvitationAdmin(admin.ModelAdmin):
    pass

class UserDeviceAdmin(admin.ModelAdmin):
    pass

class UserAccessTokenAdmin(admin.ModelAdmin):
    pass

class UserPurchasedPublicationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Role, RoleAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserPublisher, UserPublisherAdmin)
admin.site.register(UserPublisherInvitation, UserPublisherInvitationAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(UserAccessToken, UserAccessTokenAdmin)
admin.site.register(UserPurchasedPublication, UserPurchasedPublicationAdmin)
