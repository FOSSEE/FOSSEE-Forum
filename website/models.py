from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

class Question(models.Model):
    uid  = models.IntegerField()
    category = models.CharField(max_length=200)
    tutorial = models.CharField(max_length=200)
    minute_range = models.CharField(max_length=10)
    second_range = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    votes = models.IntegerField(default=0)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

class QuestionVote(models.Model):
    uid = models.IntegerField()
    question = models.ForeignKey(Question)

class QuestionComment(models.Model):
    uid = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Answer(models.Model):
    uid  = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    votes = models.IntegerField(default=0)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

class AnswerVote(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)

class AnswerComment(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    uid = models.IntegerField()
    pid = models.IntegerField()
    qid = models.IntegerField()
    rid = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

# CDEEP database created using inspectdb arg of manage.py
class TutorialDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    foss_category = models.CharField(max_length=255L)
    tutorial_name = models.CharField(max_length=600L)
    tutorial_level = models.CharField(max_length=400L)
    order_code = models.IntegerField()

    class Meta:
        db_table = 'tutorial_details'

class TutorialResources(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_detail_id = models.IntegerField()
    uid = models.IntegerField()
    language = models.CharField(max_length=50L)
    upload_time = models.DateTimeField()
    reviewer = models.CharField(max_length=400L)
    tutorial_content_id = models.IntegerField()
    tutorial_outline = models.TextField()
    tutorial_outline_uid = models.IntegerField()
    tutorial_outline_status = models.IntegerField()
    tutorial_script = models.TextField()
    tutorial_script_uid = models.IntegerField()
    tutorial_script_status = models.IntegerField()
    tutorial_script_timed = models.TextField()
    tutorial_video = models.TextField()
    tutorial_video_uid = models.IntegerField()
    tutorial_video_status = models.IntegerField()
    tutorial_status = models.CharField(max_length=50L)
    cvideo_version = models.IntegerField()
    hit_count = models.BigIntegerField()
    request_exception = models.TextField()

    class Meta:
        db_table = 'tutorial_resources'
