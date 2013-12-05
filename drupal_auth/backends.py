from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import render_to_response, get_object_or_404

User = get_user_model()

class DrupalAuthBackend(object):
    def authenticate(self, username=None, password=None):
        try:
            user = User(name='cheese')
            user.is_active = True
            user.is_authenticated = True
            return user
        except Exception, e:
            print e.message
            print "blaj"*1000

    def get_user(self, user_id):
        try:
            print "Hello"*1000
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
