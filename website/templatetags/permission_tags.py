from django import template

from website.views import admins

register = template.Library()

def can_edit(user, obj):
    if user.id == obj.user or user.id in admins:
        return True
    return False

register.filter(can_edit)
