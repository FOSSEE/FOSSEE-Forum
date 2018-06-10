from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from django_resized import ResizedImageField
from django.utils.encoding import python_2_unicode_compatible


class FossCategory(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length =50)
    def __unicode__(self):
        return self.name

class SubFossCategory(models.Model):

    parent = models.ForeignKey(FossCategory)
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return self.name

@python_2_unicode_compatible
class Question(models.Model):

    user  = models.ForeignKey(User)
    category = models.ForeignKey(FossCategory)
    sub_category = models.CharField(max_length = 200)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    userUpVotes = models.ManyToManyField(User, blank=True, related_name='postUpVotes')
    userDownVotes = models.ManyToManyField(User, blank=True, related_name='postDownVotes')
    userViews = models.ManyToManyField(User, blank=True, related_name='postViews')
    num_votes = models.IntegerField(default=0)
    is_spam = models.BooleanField(default=False)
    image = ResizedImageField(size=[400,400], upload_to="images/questions/", blank=True)

    def __unicode__(self):
             return '{0} - {1} - {2} - {3} - {4}'.format(self.id, self.category.name, self.sub_category, self.title, self.user)

    def __str__(self):
        return self.body

    class Meta:

        get_latest_by = "date_created"

class QuestionComment(models.Model):

    uid = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

@python_2_unicode_compatible
class Answer(models.Model):

    uid  = models.IntegerField()
    question = models.ForeignKey(Question)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    userUpVotes = models.ManyToManyField(User, blank=True, related_name='postAnswerUpVotes')
    userDownVotes = models.ManyToManyField(User, blank=True, related_name='postAnswerDownVotes')
    upvotes = models.IntegerField(default=0)
    num_votes = models.IntegerField(default=0)
    is_spam = models.BooleanField(default=False)
    image = ResizedImageField(size=[400,400], upload_to="images/answers/", blank=True)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user

    def __unicode__(self):
             return 'Answer - {0} - {1}'.format(self.question.category.name, self.question.title)

    def __str__(self):
        return self.body

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
    qid = models.IntegerField()
    aid = models.IntegerField(default=0)
    cid = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
        
class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    image = ResizedImageField(size=[400,400], upload_to="images/profiles/", blank=True)
    
    class Meta:
        app_label = 'website'

class ModeratorGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    category = models.ForeignKey(FossCategory)