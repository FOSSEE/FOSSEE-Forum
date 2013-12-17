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
    url(r'^user/(?P<user_id>\d+)/notifications/$', 'website.views.user_notifications', name='user_notifications'),
    url(r'^user/(?P<user_id>\d+)/questions/$', 'website.views.user_questions', name='user_questions'),
    url(r'^user/(?P<user_id>\d+)/replies/$', 'website.views.user_replies', name='user_replies'),
    url(r'^clear-notifications/$', 'website.views.clear_notifications', name='clear_notifications'),
    url(r'^search/$', 'website.views.search', name='search'),

    # Ajax helpers
    url(r'^ajax-tutorials/$', 'website.views.ajax_tutorials', name='ajax_tutorials'),
    url(r'^ajax-duration/$', 'website.views.ajax_duration', name='ajax_duration'),
    url(r'^ajax-question-update/$', 'website.views.ajax_question_update', name='ajax_question_update'),
    url(r'^ajax-reply-update/$', 'website.views.ajax_reply_update', name='ajax_reply_update'),
    url(r'^ajax-similar-questions/$', 'website.views.ajax_similar_questions', name='ajax_similar_questions'),
    url(r'^ajax-notification-remove/$', 'website.views.ajax_notification_remove', name='ajax_notification_remove'),
    url(r'^ajax-keyword-search/$', 'website.views.ajax_keyword_search', name='ajax_keyword_search'),
    url(r'^ajax-time-search/$', 'website.views.ajax_time_search', name='ajax_time_search'),
)
