from django.contrib.auth.models import User

from website.models import Test

class DrupalAuthBackend:
    def authenticate(self, username=None, password=None):
        user = User.objects.get(username='admin')
        return user
