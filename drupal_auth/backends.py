import hashlib

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import render_to_response, get_object_or_404

User = get_user_model()

class DrupalAuthBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            p = hashlib.md5()
            p.update(password)
            if user.password == p.hexdigest():
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
