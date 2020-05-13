from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [

    path('', views.home, name='home'),
    path('questions/', views.questions, name='questions'),
    path('question/<int:question_id>/', views.get_question, name='get_question'),

    path('new-question/', views.new_question, name='new_question'),
    path('question-answer/<int:question_id>/', views.question_answer, name='question_answer'),
    path('answer-comment/<int:answer_id>/', views.answer_comment, name='answer_comment'),

    path('question/edit/<int:question_id>/', views.edit_question, name='edit_question'),
    path('answer-update/', views.answer_update, name='answer_update'),
    path('answer-comment-update/', views.answer_comment_update, name='answer_comment_update'),

    path('approve_spam_question/<int:question_id>/', views.approve_spam_question, name='approve_spam_question'),
    path('mark_answer_spam/<int:answer_id>/', views.mark_answer_spam, name='mark_answer_spam'),
    path('mark_comment_spam/<int:comment_id>/', views.mark_comment_spam, name='mark_comment_spam'),

    path('question/delete/<int:question_id>/', views.question_delete, name='question_delete'),
    path('answer_delete/<int:answer_id>/', views.answer_delete, name='answer_delete'),
    path('comment_delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),

    path('question_restore/<int:question_id>/', views.question_restore, name='question_restore'),
    path('answer_restore/<int:answer_id>/', views.answer_restore, name='answer_restore'),
    path('comment_restore/<int:comment_id>/', views.comment_restore, name='comment_restore'),

    path('search/', views.search, name='search'),
    path('filter/<str:category>/', views.filter, name='filter'),
    path('filter/<str:category>/<str:tutorial>/', views.filter, name='filter'),
    
    path('user/<int:user_id>/notifications/', views.user_notifications, name='user_notifications'),
    path('clear-notifications/', views.clear_notifications, name='clear_notifications'),


    # Moderator Panel
    path('moderator/', views.moderator_home, name='moderator_home'),
    path('moderator/activate/', views.moderator_activate, name='moderator_activate'),
    path('moderator/deactivate/', views.moderator_deactivate, name='moderator_deactivate'),
    path('moderator/questions/', views.moderator_questions, name='moderator_questions'),
    path('moderator/unanswered/', views.moderator_unanswered, name='moderator_unanswered'),
    path('moderator/train_spam_filter/', views.train_spam_filter, name='train_spam_filter'),


    # AJAX
    path('ajax-tutorials/', views.ajax_tutorials, name='ajax_tutorials'),
    path('ajax-notification-remove/', views.ajax_notification_remove, name='ajax_notification_remove'),
    path('ajax-keyword-search/', views.ajax_keyword_search, name='ajax_keyword_search'),
    path('ajax-vote-post/', views.ajax_vote_post, name='ajax_vote_post'),
    path('ajax-ans-vote-post/', views.ajax_ans_vote_post, name='ajax_ans_vote_post'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)