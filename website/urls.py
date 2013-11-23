from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^category/(?P<category>.+)/$', 'website.views.fetch_tutorials', name='fetch_tutorials'),
    url(r'^tutorial/(?P<category>.+)/(?P<tutorial>.+)/$', 'website.views.fetch_posts', name='fetch_posts'),
    url(r'^post/(?P<post_id>\d+)$', 'website.views.get_post', name='get_post'),
    url(r'^new-post/$', 'website.views.new_post', name='new_post'),
)
