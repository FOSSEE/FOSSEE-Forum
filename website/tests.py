import unittest
from django.utils import timezone
from django.contrib.auth.models import User, Group
from .models import FossCategory, Question, Answer, AnswerComment, Notification, Profile

def create_question(title, body, is_spam = 0, category_id = 1):
    user = User.objects.get(id = 758)
    category = FossCategory.objects.get(id = category_id)
    return Question.objects.create(title = title, body = body, is_spam = is_spam,\
                                    category = category, user = user)

