from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^question/(?P<question_id>\d+)/$', 'website.views.get_question', name='get_question'),
    url(r'^filter/(?P<category>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/(?P<second_range>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^new-question/$', 'website.views.new_question', name='new_question'),
    
    # Ajax helpers
    url(r'^ajax-tutorials/$', 'website.views.ajax_tutorials', name='ajax_tutorials'),
    url(r'^ajax-duration/$', 'website.views.ajax_duration', name='ajax_duration'),
)
