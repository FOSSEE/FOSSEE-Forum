from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

#from drupal_auth.managers import DrupalUserManager
class Users(AbstractBaseUser):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100L, unique=True)
    email = models.CharField(max_length=100L, unique=True)
    USERNAME_FIELD = 'username'
    class Meta:
        db_table = 'auth_user'
