from django.conf.urls import patterns, include, url
from moderator import views

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name="home"),
    url(r'^questions/$', views.questions, name="questions"),
    url(r'^unanswered_questions/$', views.unanswered_questions, name='unanswered_questions'),
    url(r'^questions/delete_question/$', views.delete_question, name="delete_question"),
    url(r'^category/$', views.category, name='category'),
    url(r'^user/$', views.User_info, name='user'),
    url(r'^user/user_update/$', views.user_update, name='user_update'),
    url(r'^category/(?P<category_id>\d+)/$', views.category_form, name='category-form'),
    url(r'^category/new_category/$', views.new_category, name='new_category'),
    url(r'^questions/get_question/(?P<question_id>\d+)/$', views.get_question, name="get_question")
    )
