from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('membership.views',
    
    url(r'^welcome/$', 'view_user_welcome', name='view_user_welcome'),
)
