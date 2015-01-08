from django import template

from website.models import Question, Answer, Notification
from website.helpers import prettify
from django.conf import settings
import os.path

register = template.Library()

def get_category_image(category):
    base_path = settings.PROJECT_DIR + '/static/website/images/'
    file_name = category.replace(' ', '-') + '.jpg'
    file_path = base_path + file_name
    if os.path.isfile(file_path):
        return 'website/images/' + file_name
    return False

register.filter('get_category_image', get_category_image)
# imported from website/helpers
register.simple_tag(prettify)
