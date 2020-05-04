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

    path('vote_post/', views.vote_post, name='vote_post'),
    path('ans_vote_post/', views.ans_vote_post, name='ans_vote_post'),
    path('mark_answer_spam/<int:answer_id>/', views.mark_answer_spam, name='mark_answer_spam'),


    # Moderator Panel
    path('moderator/', views.moderator_home, name='moderator_home'),
    path('moderator/questions/', views.moderator_questions, name='moderator_questions'),
    path('moderator/unanswered/', views.moderator_unanswered, name='moderator_unanswered'),
    path('moderator/train_spam_filter/', views.train_spam_filter, name='train_spam_filter'),


    # AJAX
    path('ajax-tutorials/', views.ajax_tutorials, name='ajax_tutorials'),
    path('ajax-answer-update/', views.ajax_answer_update, name='ajax_answer_update'),
    path('ajax-answer-comment-update/', views.ajax_answer_comment_update, name='ajax_answer_comment_update'),
    path('ajax-notification-remove/', views.ajax_notification_remove, name='ajax_notification_remove'),
    path('ajax-keyword-search/', views.ajax_keyword_search, name='ajax_keyword_search'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)