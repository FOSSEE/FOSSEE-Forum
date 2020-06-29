from django.conf import settings
from .views import admins


def admin_processor(request):
    return {'admins': admins}


def booleans():
    return {
        'True': True,
        'False': False,
    }


def moderator_activated(request):
    """
    Return False for Anonymous Users.
    Return the value of MODERATOR_ACTIVATED session variable for Authenticated
    Users.
    """
    return {'MODERATOR_ACTIVATED': request.session.get(
        'MODERATOR_ACTIVATED', False)}
