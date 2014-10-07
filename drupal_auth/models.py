from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from drupal_auth.managers import DrupalUserManager

class Users(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100L, unique=True)
    password = models.CharField(max_length=32L)
    email = models.CharField(max_length=100L)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = DrupalUserManager()

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'mdl_user'

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_staff(self):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
