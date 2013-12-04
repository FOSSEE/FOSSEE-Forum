from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

class DrupalUserManager(BaseUserManager):
    def create_user(self, password=None):
        user = self.model()
        if not email:
            raise ValueError('Users must have an email address')

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password):
        user = self.model()
        user.username = username
        user.password = password
        user.is_admin = True
        user.save(using=self._db)
        return user



























