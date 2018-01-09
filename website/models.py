from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager


class FossCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length=50)
    default_tags = TaggableManager()
    def __unicode__(self):
        return self.name


class SubFossCategory(models.Model):
    parent = models.ForeignKey(FossCategory)
    name = models.CharField(max_length=100)
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
    user = models.ForeignKey(User)
    category = models.ForeignKey(FossCategory)
    sub_category = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    userUpVotes = models.ManyToManyField(User,
                                         blank=True,
                                         related_name='postUpVotes')
    userDownVotes = models.ManyToManyField(User,
                                           blank=True,
                                           related_name='postDownVotes')
    num_votes = models.IntegerField(default=0)
    tags = TaggableManager()

    def __unicode__(self):
        return '{0} - {1} - {2} - {3} - {4}'.format(self.id,
                                                    self.category.name,
                                                    self.sub_category,
                                                    self.title,
                                                    self.user)

    def __str__(self):
        return self.body

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
    uid = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    userUpVotes = models.ManyToManyField(User,
                                         blank=True,
                                         related_name='postAnswerUpVotes')
    userDownVotes = models.ManyToManyField(User,
                                           blank=True,
                                           related_name='postAnswerDownVotes')
    upvotes = models.IntegerField(default=0)
    num_votes = models.IntegerField(default=0)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user

    def __unicode__(self):
        return 'Answer - {0} - {1}'.format(self.question.category.name,
                                           self.question.title)

    def __str__(self):
        return self.body


class AnswerVote(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)


class AnswerComment(models.Model):
    uid = models.IntegerField()
    answer = models.ForeignKey(Answer)
    body = models.TextField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user


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


class Profile(models.Model):
    user = models.ForeignKey(User)
    confirmation_code = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'website'
