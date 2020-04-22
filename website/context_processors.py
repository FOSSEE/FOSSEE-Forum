from website.views import admins
from django.conf import settings


def admin_processor(request):
    return {'admins': admins}


def booleans():
    return {
        'True': True,
        'False': False,
    }


def moderator_activated(request):
    # Always returns False for Anonymous Users and respective value for Authenticated Users
    return {'MODERATOR_ACTIVATED': request.session.get('MODERATOR_ACTIVATED', False)}
