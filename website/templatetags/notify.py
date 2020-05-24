from django import template

from website.models import Question, Answer, Notification

register = template.Library()

# Display the notifications of the user
@register.inclusion_tag('website/templates/notify.html')
def get_notification(nid):
    notification = Notification.objects.get(pk=nid)
    question = Question.objects.get(pk=notification.qid)
    answer = Answer.objects.get(pk=notification.aid)
    context = {
        'notification': notification,
        'question': question,
        'answer': answer,
    }
    return context


@register.simple_tag
def notification_count(user_id):
    count = Notification.objects.filter(uid=user_id).count()
    return count


# retriving the latest post of a category
@register.inclusion_tag('website/templates/latest_question.html')
def latest_question(category):
    question = None
    try:
        question = Question.objects.filter(
            category=category, is_active=True).order_by('-date_created')[0]
    except BaseException:
        pass
    context = {
        'question': question
    }
    return context
