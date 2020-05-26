from builtins import range
from django import template
from website.models import Question, Answer

register = template.Library()

# Question/Answer Count
@register.simple_tag
def category_question_count(category):
    """Return the number of active and non-spam questions in the category."""
    category_question_count = Question.objects.filter(category=category, is_active=True, is_spam=False).count()
    return category_question_count

@register.simple_tag
def answer_count(question):
    """Return the number of active and non-spam answers to a question."""
    return question.answer_set.filter(is_active=True, is_spam=False).count()

@register.simple_tag
def total_question_count():
    """Return total number of active and non-spam questions of unhidden categories on forum."""
    count = Question.objects.filter(is_active=True, is_spam=False, category__hidden=False).count()
    return count

@register.simple_tag
def total_answer_count():
    """Return total number of active and non-spam answers in unhidden categories on forum."""
    count = Answer.objects.filter(is_active=True, is_spam=False, question__category__hidden=False).count()
    return count


# Implementing range(x) function in templates
@register.filter
def get_range(value, arg=''):
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
        raise TypeError(
            'get_range() takes maximum 2 arguments, {} given'.format(n))
    return list(range(start, limit, step))


# Implementing increment and decrement functions
@register.filter
def inc(value, arg=1):
    return value + int(arg)

@register.filter
def dec(value, arg=1):
    return value - int(arg)


# Implementing calculator for templates
@register.filter
def add(value, arg=0):
    return value + int(arg)

@register.filter
def sub(value, arg=0):
    return value - int(arg)

@register.filter
def mul(value, arg=1):
    return value * int(arg)

@register.filter
def div(value, arg=1):
    return value / arg


# Get length of array
@register.simple_tag
def length(array):
    return len(array)
