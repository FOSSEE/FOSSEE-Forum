from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^question/(?P<question_id>\d+)/$', 'website.views.get_question', name='get_question'),
    url(r'^question-reply/$', 'website.views.question_reply', name='question_reply'),
    url(r'^filter/(?P<category>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/(?P<second_range>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^new-question/$', 'website.views.new_question', name='new_question'),
    
    # Ajax helpers
    url(r'^ajax-tutorials/$', 'website.views.ajax_tutorials', name='ajax_tutorials'),
    url(r'^ajax-duration/$', 'website.views.ajax_duration', name='ajax_duration'),
    url(r'^ajax-question-update/$', 'website.views.ajax_question_update', name='ajax_question_update'),
)
