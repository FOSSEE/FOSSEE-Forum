import re
from django import template
from website.models import Question, Answer, Notification
from django.conf import settings
import os.path

register = template.Library()

# Cleaning a string
@register.simple_tag
def prettify(string):
    string = string.lower()
    string = string.replace('-', ' ')
    string = string.strip()
    string = string.replace(' ', '-')
    string = re.sub(r'[^A-Za-z0-9\-]+', '', string)
    string = re.sub('-+', '-', string)
    return string

# Getting only the 100 most recent questions
@register.filter
def get_recent_questions(questions):
    return questions

# Concatenating two strings in template
@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
