from builtins import object
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from django_resized import ResizedImageField
from ckeditor.fields import RichTextField
from django.db.models.signals import post_delete
from django.dispatch import receiver


class FossCategory(models.Model):

    name = models.CharField(max_length=100, default='None', blank=True)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    email = models.CharField(max_length=50)
    disabled = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    image = ResizedImageField(
        size=[
            800,
            800],
        upload_to="images/fossCategory/",
        blank=True)

    def __str__(self):
        return self.name


class ModeratorGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    category = models.OneToOneField(FossCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.group.name + " - " + self.category.name


class AdvertiseBanner(models.Model):
    body = models.TextField(default='Null')


class SubFossCategory(models.Model):

    parent = models.ForeignKey(FossCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='None', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(FossCategory, on_delete=models.CASCADE)
    sub_category = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200)
    body = RichTextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=1)
    userUpVotes = models.ManyToManyField(
        User, blank=True, related_name='postUpVotes', default=0)
    userDownVotes = models.ManyToManyField(
        User, blank=True, related_name='postDownVotes', default=0)
    userViews = models.ManyToManyField(
        User, blank=True, related_name='postViews')
    num_votes = models.IntegerField(default=0)
    is_spam = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notif_flag = models.IntegerField(default=0)
    is_answering_closed = models.BooleanField(default=False)
    image = ResizedImageField(
        size=[
            800,
            800],
        upload_to="images/questions/",
        blank=True)

    def __str__(self):
        return '{0} - {1} - {2} - {3} - {4}'.format(
            self.id, self.category.name, self.sub_category, self.title,
            self.user)

    class Meta(object):

        get_latest_by = "date_created"


class Answer(models.Model):

    uid = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = RichTextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    userUpVotes = models.ManyToManyField(
        User, blank=True, related_name='postAnswerUpVotes', default=0)
    userDownVotes = models.ManyToManyField(
        User, blank=True, related_name='postAnswerDownVotes', default=0)
    num_votes = models.IntegerField(default=0)
    is_spam = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notif_flag = models.IntegerField(default=0)
    image = ResizedImageField(
        size=[
            800,
            800],
        upload_to="images/answers/",
        blank=True)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.question.category.name,
                                        self.question.title, self.body)


@receiver(post_delete, sender=Question)
@receiver(post_delete, sender=Answer)
@receiver(post_delete, sender=FossCategory)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


class AnswerComment(models.Model):

    uid = models.IntegerField()
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    body = models.TextField(blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    is_spam = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notif_flag = models.IntegerField(default=0)

    def user(self):
        user = User.objects.get(id=self.uid)
        return user


class Notification(models.Model):

    uid = models.IntegerField()   # User id
    qid = models.IntegerField()   # Question id
    pid = models.IntegerField(default=0)
    aid = models.IntegerField(default=0)   # Answer id
    cid = models.IntegerField(default=0)   # Comment id
    date_created = models.DateTimeField(auto_now_add=True)


class Scheduled_Auto_Mail(models.Model):
    mail_sent_date = models.CharField(max_length=255)
    is_sent = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    confirmation_code = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        app_label = 'website'
