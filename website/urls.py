from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from website import views

urlpatterns = [
    
    url(r'^$', views.home, name='home'),
    url(r'^questions/$', views.questions, name='questions'),
    url(r'^question/(?P<question_id>\d+)/$', views.get_question, name='get_question'),
    url(r'^question/(?P<question_id>\d+)/(?P<pretty_url>.+)/$', views.get_question, name='get_question'),
    url(r'^question/edit/(?P<question_id>\d+)/$', views.edit_question, name='edit_question'),
    url(r'^question-answer/(?P<question_id>\d+)/$', views.question_answer, name='question_answer'),
    url(r'^answer-comment/$', views.answer_comment, name='answer_comment'),
    url(r'^filter/(?P<category>[^/]+)/$', views.filter, name='filter'),
    url(r'^filter/(?P<category>[^/]+)/(?P<tutorial>[^/]+)/$', views.filter, name='filter'),
    url(r'^new-question/$', views.new_question, name='new_question'),
    url(r'^user/(?P<user_id>\d+)/notifications/$', views.user_notifications, name='user_notifications'),
    url(r'^clear-notifications/$', views.clear_notifications, name='clear_notifications'),
    url(r'^search/$', views.search, name='search'),
    url(r'^vote_post/$', views.vote_post, name='vote_post'),
    url(r'^ans_vote_post/$', views.ans_vote_post, name='ans_vote_post'),
    url(r'^question/delete/(?P<question_id>\d+)/$', views.question_delete, name='question_delete'),
    url(r'^mark_answer_spam/(?P<answer_id>\d+)/$', views.mark_answer_spam, name='mark_answer_spam'),
    url(r'^answer_delete/(?P<answer_id>\d+)/$', views.answer_delete, name='answer_delete'),

    # Moderator panel
    url(r'^moderator/$', views.moderator_home, name='moderator_home'),
    url(r'^moderator/questions/$', views.moderator_questions, name='moderator_questions'),
    url(r'^moderator/unanswered/$', views.moderator_unanswered, name='moderator_unanswered'),
    
    # Ajax helpers
    url(r'^ajax-tutorials/$', views.ajax_tutorials, name='ajax_tutorials'),
    url(r'^ajax-answer-update/$', views.ajax_answer_update, name='ajax_answer_update'),
    url(r'^ajax-answer-comment-update/$', views.ajax_answer_comment_update, name='ajax_answer_comment_update'),
    url(r'^ajax-notification-remove/$', views.ajax_notification_remove, name='ajax_notification_remove'),
    url(r'^ajax-keyword-search/$', views.ajax_keyword_search, name='ajax_keyword_search'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)