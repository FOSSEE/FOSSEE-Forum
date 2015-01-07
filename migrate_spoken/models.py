from django.db import models

class OldUsers(models.Model):
    uid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=60)
    pass_field = models.CharField(db_column='pass', max_length=32) # Field renamed because it was a Python reserved word.
    mail = models.CharField(max_length=64, blank=True)
    mode = models.IntegerField()
    sort = models.IntegerField(blank=True, null=True)
    threshold = models.IntegerField(blank=True, null=True)
    theme = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    signature_format = models.IntegerField()
    created = models.IntegerField()
    access = models.IntegerField()
    login = models.IntegerField()
    status = models.IntegerField()
    timezone = models.CharField(max_length=8, blank=True)
    language = models.CharField(max_length=12)
    picture = models.CharField(max_length=255)
    init = models.CharField(max_length=64, blank=True)
    data = models.TextField(blank=True)
    last_login = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = 'users'

