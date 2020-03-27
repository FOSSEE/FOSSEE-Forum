from django import template

register = template.Library()


def can_edit(user, obj):
    try:
        if user == obj.user or user.id == obj.uid:
            return True
        else:
            return False
    except BaseException:
        return False


register.filter(can_edit)


def is_moderator(user):
    print(user, "---template---")
    try:
        if user.groups.count() > 0:
            print(user.groups.count(), "====")
            return True
        else:
            print("------------")
            print("No group")
            print("------------")
            return False
    except BaseException as e:
        print("------------")
        print(e)
        print("------------")
        return False


register.filter(is_moderator)


def comment_id(answer):
    return "comment" + str(answer.id)


register.filter(comment_id)


def havenot_comments(answer):
    return(not answer.answercomment_set.filter(is_active=True).exists())


register.filter(havenot_comments)


def can_delete(answer, comment_id):
    comments = answer.answercomment_set.filter(is_active=True)
    for x in comments:
        if x.id > comment_id:
            return False
    return True


register.filter(can_delete)
