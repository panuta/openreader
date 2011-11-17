from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'auth_login', name='auth_login'),

    url(r'^accounts/welcome/$', 'view_user_welcome', name='view_user_welcome'),

    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^my/account/$', 'view_my_account', name='view_my_account'),
    url(r'^my/account/change_password/$', 'change_my_account_password', name='change_my_account_password'),
)