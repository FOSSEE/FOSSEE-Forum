from website.models import *


def social_authentication_profile(backend, user, response, *args, **kwargs):
    """Profile creation when login occours through social login options"""

    # divided based on different backends for furthur addition of backend specific features
    if backend.name == "google-oauth2":
        u = User.objects.get(username=user)
        p = Profile.objects.get_or_create(user=u)

    if backend.name == "facebook":
        u = User.objects.get(username=user)
        p = Profile.objects.get_or_create(user=u)