from website.views import admins

def admin_processor(request):
    return {'admins': admins}

def booleans():
    return {
        'True': True,
        'False': False,
    }
