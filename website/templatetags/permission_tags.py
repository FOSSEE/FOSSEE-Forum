from django import template

register = template.Library()

@register.filter
def is_author(user, obj):
    try:
        if user == obj.user or user.id == obj.uid:
            return True
        else:
            return False
    except BaseException:
        return False


@register.filter
def is_moderator(user):
    try:
        if user.groups.count() > 0:
            return True
        else:
            print("------------")
            print("No group")
            print("------------")
            return False
    except BaseException as e:
        print("------Error------")
        print(e)
        print("------------")
        return False


@register.filter
def comment_id(answer):
    return "comment" + str(answer.id)


@register.filter
def havenot_comments(answer):
    return(not answer.answercomment_set.filter(is_active=True).exists())


@register.filter
def can_delete(answer, comment_id):
    comments = answer.answercomment_set.filter(is_active=True)
    for x in comments:
        if x.id > comment_id:
            return False
    return True
