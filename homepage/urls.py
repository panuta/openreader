from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('homepage.views',
    
    url(r'^$', 'view_homepage', name='view_homepage'),
)
