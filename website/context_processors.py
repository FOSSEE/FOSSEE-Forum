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
    return {'MODERATOR_ACTIVATED': settings.MODERATOR_ACTIVATED}