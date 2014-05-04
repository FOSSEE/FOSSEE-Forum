from django import template

from website.models import Question, Answer, Notification
from website.helpers import prettify

register = template.Library()

# imported from website/helpers
register.simple_tag(prettify)
