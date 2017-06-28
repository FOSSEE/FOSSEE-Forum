from website.models import Question, Answer, Notification, \
    AnswerComment, FossCategory, Profile, SubFossCategory, FossCategory
from django.contrib.auth.models import User
from forms import Category, Emails
from django.core.context_processors import csrf
from forums import settings
import os,re

def delete_question_util(ques_id):
    """helper function for deleting questions"""

    for ans in Answer.objects.filter(question_id=ques_id):

        # delete all the answers

        delete_answer_util(ans.id)

    # delete the qustion with recieved question_id

    question = Question.objects.get(id=ques_id)
    user_email = User.objects.get(id=question.user_id).email
    question_title = question.title
    question.userDownVotes.clear()
    question.userUpVotes.clear()

    # delete all the images
    pat = re.compile (r'<img [^>]*src="([^"]+)')
    images = pat.findall(question.body)
    for image in images:
        if os.path.exists(image[1:]):
            os.remove(image[1:])

    question.delete()

    return (question_title, user_email)


def delete_comment_util(comment_id):
    """helper function for deleting comments"""

    comment = AnswerComment.objects.get(id=comment_id)
    body = comment.body
    comment.delete()
    return body


def delete_answer_util(answer_id):
    """helper function for deleting answers"""

    # delete all the comments

    for comment in AnswerComment.objects.filter(answer_id=answer_id):
        delete_comment_util(comment.id)

    ans = Answer.objects.get(id=answer_id)
    body = ans.body

    # delete all the votes

    ans.userDownVotes.clear()
    ans.userUpVotes.clear()

    # delete all the images
    pat = re.compile (r'<img [^>]*src="([^"]+)')
    images = pat.findall(ans.body)
    for image in images:
        if os.path.exists(image[1:]):
            os.remove(image[1:])
    ans.delete()
    return body