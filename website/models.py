from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    user  = models.ForeignKey(User)
    category = models.CharField(max_length=200)
    tutorial = models.CharField(max_length=200)
    minute_start = models.IntegerField()
    minute_end = models.IntegerField()
    second_start = models.IntegerField()
    second_end = models.IntegerField()
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

class Reply(models.Model):
    user  = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    title = models.CharField(max_length=200)
    body = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

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
