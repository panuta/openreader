from django.contrib import admin
from publication.models import *

class PublicationAdmin(admin.ModelAdmin):
    pass

class PublicationNoticeAdmin(admin.ModelAdmin):
    pass

class UserPurchasedPublicationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Publication, PublicationAdmin)
admin.site.register(PublicationNotice, PublicationNoticeAdmin)
admin.site.register(UserPurchasedPublication, UserPurchasedPublicationAdmin)
