from builtins import range
from django import template

from website.models import Question, Answer

register = template.Library()

# Counts the number of questions in <category>
def category_question_count(category):
    category_question_count = Question.objects.filter(category = category).count()
    return category_question_count
register.simple_tag(category_question_count)

# Implementing range(x) function in templates
def get_range(value, arg = ''):
    args = arg.split(', ')
    n = len(args)

    if n == 0 or arg == '':
        # if no arguments set value as limit
        start = 0
        limit = value
        step = 1
    elif n == 1:
        start = int(args[0])
        limit = value
        step = 1
    elif n == 2:
        start = int(args[0])
        limit = value
        step = int(args[1])
    else:
        raise TypeError('get_range() takes maximum 2 arguments, {} given'.format(n))
    return list(range(start, limit, step))
register.filter('get_range', get_range)

# Implementing increment and decrement functions
def inc(value, arg = 1):
    return value + int(arg)
register.filter('inc', inc)

def dec(value, arg = 1):
    return value-int(arg)
register.filter('dec', dec)

# Implementing calculator for templates
def add(value, arg = 0):
    return value + int(arg)
register.filter('add', add)

def sub(value, arg = 0):
    return value - int(arg)
register.filter('sub', sub)

def mul(value, arg = 1):
    return value * int(arg)
register.filter('mul', mul)

def div(value, arg = 1):
    return value/arg
register.filter('div', div)

# retriving total number of questions
def total_question_count():
    count = Question.objects.all().count()
    return count
register.simple_tag(total_question_count)

# retriving total number of answers
def total_answer_count():
    count = Answer.objects.all().count()
    return count
register.simple_tag(total_answer_count)

# Get length of array
def length(array):
    return len(array)
register.simple_tag(length)