from django import template

from website.views import admins

register = template.Library()


def can_edit(user, obj):
    try:
        if user == obj.user or user.id == obj.uid or user.id in admins:  
           return True
        else:
    	   return False
    except:
        return False


register.filter(can_edit)
