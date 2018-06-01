import re
from django import template
from website.models import Question, Answer, Notification
from django.conf import settings
import os.path

register = template.Library()

def prettify(string):
    string = string.lower()
    string = string.replace('-', ' ')
    string = string.strip()
    string = string.replace(' ', '-')
    string = re.sub('[^A-Za-z0-9\-]+', '', string)
    string = re.sub('-+', '-', string)
    return string
register.simple_tag(prettify)

def get_category_image(category):
    base_path = settings.PROJECT_DIR + '/static/website/images/'
    file_name = category.name.replace(' ', '') + '.jpg'
    file_path = base_path + file_name
    if os.path.isfile(file_path):
        return 'website/images/' + file_name
    return False
register.filter('get_category_image', get_category_image)
