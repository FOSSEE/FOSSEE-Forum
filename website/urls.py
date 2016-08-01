from django.conf.urls import patterns, include, url
from website import views

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^questions/$', 'website.views.questions', name='questions'),
    url(r'^question/(?P<question_id>\d+)/$', 'website.views.get_question', name='get_question'),
    url(r'^question/(?P<question_id>\d+)/(?P<pretty_url>.+)/$', 'website.views.get_question', name='get_question'),
    url(r'^question-answer/(?P<qid>\d+)/$', 'website.views.question_answer', name='question_answer'),
    url(r'^answer-comment/$', 'website.views.answer_comment', name='answer_comment'),
    url(r'^filter/(?P<category>[^/]+)/$', 'website.views.filter', name='filter'),
    #url(r'^filter/$', 'website.views.filter', name='filter'),
    #url(r'^filter/(?P<category>[^/]+)/$', 'website.views.filter', name='filter')
    
    #url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/$', 'website.views.filter', name='filter'),
    #url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/(?P<minute_range>[^/]+)/(?P<second_range>[^/]+)/$', 'website.views.filter', name='filter'),
    url(r'^new-question/$', 'website.views.new_question', name='new_question'),
    url(r'^user/(?P<user_id>\d+)/notifications/$', 'website.views.user_notifications', name='user_notifications'),
    url(r'^user/(?P<user_id>\d+)/questions/$', 'website.views.user_questions', name='user_questions'),
    url(r'^user/(?P<user_id>\d+)/answers/$', 'website.views.user_answers', name='user_answers'),
    url(r'^clear-notifications/$', 'website.views.clear_notifications', name='clear_notifications'),
    url(r'^search/$', 'website.views.search', name='search'),
    # url(r'^unanswerednotification/$', views.unanswered_notification, name='unanswered_notification'),
    url(r'^vote_post/$', 'website.views.vote_post', name='vote_post'),
    url(r'^ans_vote_post/$', 'website.views.ans_vote_post', name='ans_vote_post'),
    
    # Ajax helpers
    url(r'^ajax-tutorials/$', 'website.views.ajax_tutorials', name='ajax_tutorials'),
    url(r'^ajax-duration/$', 'website.views.ajax_duration', name='ajax_duration'),
    url(r'^ajax-question-update/$', 'website.views.ajax_question_update', name='ajax_question_update'),
    url(r'^ajax-details-update/$', 'website.views.ajax_details_update', name='ajax_details_update'),
    url(r'^ajax-answer-update/$', 'website.views.ajax_answer_update', name='ajax_answer_update'),
    url(r'^ajax-answer-comment-update/$', 'website.views.ajax_answer_comment_update', name='ajax_answer_comment_update'),
    url(r'^ajax-similar-questions/$', 'website.views.ajax_similar_questions', name='ajax_similar_questions'),
    url(r'^ajax-notification-remove/$', 'website.views.ajax_notification_remove', name='ajax_notification_remove'),
    url(r'^ajax-keyword-search/$', 'website.views.ajax_keyword_search', name='ajax_keyword_search'),
    url(r'^ajax-time-search/$', 'website.views.ajax_time_search', name='ajax_time_search'),
)
