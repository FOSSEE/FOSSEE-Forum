from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from website import views

app_name = 'website'

urlpatterns = [

    path('', views.home, name = 'home'),
    path('questions/', views.questions, name = 'questions'),
    path('question/<int:question_id>/', views.get_question, name = 'get_question'),
    path('question/edit/<int:question_id>/', views.edit_question, name = 'edit_question'),
    path('question-answer/<int:question_id>/', views.question_answer, name = 'question_answer'),
    path('answer-comment/', views.answer_comment, name = 'answer_comment'),
    path('filter/<str:category>/', views.filter, name = 'filter'),
    path('filter/<str:category>/<str:tutorial>/', views.filter, name = 'filter'),
    path('new-question/', views.new_question, name = 'new_question'),
    path('user/<int:user_id>/notifications/', views.user_notifications, name = 'user_notifications'),
    path('clear-notifications/', views.clear_notifications, name = 'clear_notifications'),
    path('search/', views.search, name = 'search'),
    path('vote_post/', views.vote_post, name = 'vote_post'),
    path('ans_vote_post/', views.ans_vote_post, name = 'ans_vote_post'),
    path('question/delete/<int:question_id>/', views.question_delete, name = 'question_delete'),
    path('mark_answer_spam/<int:answer_id>/', views.mark_answer_spam, name = 'mark_answer_spam'),
    path('answer_delete/<int:answer_id>/', views.answer_delete, name = 'answer_delete'),

    # Moderator panel
    path('moderator/', views.moderator_home, name = 'moderator_home'),
    path('moderator/questions/', views.moderator_questions, name = 'moderator_questions'),
    path('moderator/unanswered/', views.moderator_unanswered, name = 'moderator_unanswered'),
    path('moderator/train_spam_filter/', views.train_spam_filter, name = 'train_spam_filter'),

    # Ajax helpers
    path('ajax-tutorials/', views.ajax_tutorials, name = 'ajax_tutorials'),
    path('ajax-answer-update/', views.ajax_answer_update, name = 'ajax_answer_update'),
    path('ajax-answer-comment-delete/', views.ajax_answer_comment_delete, name = 'ajax_answer_comment_delete'),
    path('ajax-notification-remove/', views.ajax_notification_remove, name = 'ajax_notification_remove'),
    path('ajax-keyword-search/', views.ajax_keyword_search, name = 'ajax_keyword_search'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)