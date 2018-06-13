import unittest
from django.utils import timezone
from django.contrib.auth.models import User, Group
from .models import FossCategory, Question, Answer, AnswerComment, Notification, Profile

def create_question(title, body, category_id = 1, uid = 758):
    """ Function to create sample question """
    user = User.objects.get(id = uid)
    category = FossCategory.objects.get(id = category_id)
    return Question.objects.create(title = title, body = body, category = category, user = user)

def create_answer(body, is_spam = 0, question_id = 1, uid = 758):
    """ Function to create sample answers """
    question = Question.objects.get(id = question_id)
    return Answer.objects.create(body = body, question = question, uid = uid) 

def create_answercomment(body, answer_id = 1, uid = 758):
    """ Function to create sample answer comments """
    answer = Answer.objects.get(id = answer_id)
    return AnswerComment.objects.create(body = body, answer = answer, uid = uid)

def create_notification(uid = 758, qid = 1):
    """ Function to create sample notification """
    return Notification.objects.create(uid = uid, qid = qid)

def create_profile():
    """ Function to create sample profile """
    user = User.objects.create_user("johndoe", "johndoe@example.com", "johndoe")
    return Profile.objects.create(user)
