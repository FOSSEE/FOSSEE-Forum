from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

class FossCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name

class Issue(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name

class Question(models.Model):
    user  = models.ForeignKey(User)
    category = models.ForeignKey(FossCategory)
    tutorial = models.ForeignKey(Issue)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    # votes = models.IntegerField(default=0)

    class Meta:
        get_latest_by = "date_created"

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
    # votes = models.IntegerField(default=0)

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

    def user(self):
        user = User.objects.get(id=self.uid)
        return user.username

class Notification(models.Model):
    uid = models.IntegerField()
    pid = models.IntegerField()
    qid = models.IntegerField()
    aid = models.IntegerField(default=0)
    cid = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def poster(self):
        user = User.objects.get(id=self.pid)
        return user.username
