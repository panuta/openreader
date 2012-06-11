from django.conf.urls import patterns, url

urlpatterns = patterns('accounts.views',
    url(r'^accounts/login/$', 'auth_login', name='auth_login'),
    url(r'^accounts/welcome/$', 'view_user_welcome', name='view_user_welcome'),
)