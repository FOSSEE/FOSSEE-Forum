import re

from django import template

from website.models import Question, Answer

register = template.Library()

# Showing/Hiding nice-bar on pages
def is_nice_bar_visible(request):
    try:
        if request.path == '/':
            return True
        elif "Oscad" in request.path:
            return True
        elif "/question/" in request.path:
            try:
                question_id = request.path[1:-1].split('/')
                question_id = int(question_id[1])
                question = Question.objects.get(pk=question_id)
                if question.category == "Oscad":
                    return True
            except:
                return False
    except:
        return False
    return False
register.filter('is_nice_bar_visible', is_nice_bar_visible)
