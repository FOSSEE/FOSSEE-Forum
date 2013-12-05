from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from drupal_auth.managers import DrupalUserManager

class Users(models.Model):
    name = models.CharField(max_length=60L, unique=True, primary_key=True)
    pass_field = models.CharField(max_length=32L, db_column='pass') # Field renamed because it was a Python reserved word.
    last_login = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
    objects = DrupalUserManager()

    class Meta:
        db_table = 'users'

    def is_authenticated(self):
        return True
#class Test(AbstractBaseUser):
#    username = models.CharField(max_length=40, unique=True, db_index=True)
#    USERNAME_FIELD = 'username'
#    REQUIRED_FIELDS = []
#
#    objects = DrupalUserManager()
