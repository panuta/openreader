from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'login', name='login'),

    url(r'^accounts/welcome/$', 'view_user_welcome', name='view_user_welcome'),

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),    
    url(r'^my/account/$', 'view_my_account', name='view_my_account'),
)