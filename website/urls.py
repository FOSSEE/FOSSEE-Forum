from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^category/(?P<category>.+)/$', 'website.views.fetch_tutorials', name='fetch_tutorials'),
    url(r'^tutorial/(?P<category>.+)/(?P<tutorial>.+)/$', 'website.views.fetch_questions', name='fetch_questions'),
    url(r'^question/(?P<question_id>\d+)$', 'website.views.get_question', name='get_question'),
    url(r'^new-question/$', 'website.views.new_question', name='new_question'),
    
    # Ajax helpers
    url(r'^ajax-tutorials/$', 'website.views.ajax_tutorials', name='ajax_tutorials'),
    url(r'^ajax-duration/$', 'website.views.ajax_duration', name='ajax_duration'),
)
