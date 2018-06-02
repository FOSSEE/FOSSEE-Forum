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
    string = re.sub('[^A-Za-z0-9\-]+', '', string)
    string = re.sub('-+', '-', string)
    return string
register.simple_tag(prettify)

# Getting the category image
def get_category_image(category):
    base_path = settings.PROJECT_DIR + '/static/website/images/'
    file_name = category.name.replace(' ', '') + '.jpg'
    file_path = base_path + file_name
    if os.path.isfile(file_path):
        return 'website/images/' + file_name
    return False
register.filter('get_category_image', get_category_image)

# Getting only the 10 most recent questions
def get_recent_questions(questions):
    return questions[:10]
register.filter('get_recent_questions', get_recent_questions)