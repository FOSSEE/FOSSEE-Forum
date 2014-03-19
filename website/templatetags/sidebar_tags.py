from django import template

from website.models import Question, Answer

register = template.Library()

def recent_questions():
    recent_questions = Question.objects.all().order_by('-id')[:5]
    return {'recent_questions': recent_questions}

register.inclusion_tag('website/templates/recent_questions.html')(recent_questions)
