import re
from django import template
from website.models import Question, Answer, Notification
from django.conf import settings
import os.path

register = template.Library()

# Cleaning a string


def prettify(string):
    string = string.lower()
    string = string.replace('-', ' ')
    string = string.strip()
    string = string.replace(' ', '-')
    string = re.sub(r'[^A-Za-z0-9\-]+', '', string)
    string = re.sub('-+', '-', string)
    return string


register.simple_tag(prettify)


# Getting only the 100 most recent questions


def get_recent_questions(questions):
    return questions[:100]


register.filter('get_recent_questions', get_recent_questions)
