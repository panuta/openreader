from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'login', name='login'),

    url(r'^welcome/$', 'view_user_welcome', name='view_user_welcome'),

)