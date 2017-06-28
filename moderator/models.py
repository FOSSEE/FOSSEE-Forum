from django.conf import settings
from django.db import models


# Create your models here.
class NotificationEmail(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

