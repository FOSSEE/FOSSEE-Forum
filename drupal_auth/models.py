from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from drupal_auth.managers import DrupalUserManager

class Users(models.Model):
    id = models.IntegerField(primary_key=True, db_column='uid')
    username = models.CharField(max_length=60L, unique=True, db_column='name')
    password = models.CharField(max_length=32L, db_column='pass') # Field renamed because it was a Python reserved word.
    email = models.CharField(max_length=200L, db_column='mail')
    last_login = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = DrupalUserManager()

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'users'

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
