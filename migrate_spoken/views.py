from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from website.models import Question, Answer, AnswerComment, Notification
from migrate_spoken.models import OldUsers
from spoken_auth.models import Users
# Create your views here.

def get_old_user(uid):
    try:
        return OldUsers.objects.get(pk = uid)
    except Exception, e:
        return None

def get_current_user_from_old_email(mail):
    try:
        return Users.objects.get(email = mail)
    except Exception, e:
        print e
        return None

def get_current_user_id_from_old_uerid(uid):
    old_user = get_old_user(uid)
    if old_user:
        #print old_user.uid, " => ", old_user.mail
        current_user = get_current_user_from_old_email(old_user.mail)
        if current_user:
            #print current_user.id, " => ", current_user.email
            return current_user
    return None

def chenage_drupal_userid_spoken(request):
    models = ['Question', 'Answer', 'AnswerComment', 'Notification']
    for model in models:
        model = eval(model)
        collection = model.objects.all()
        for c in collection:
            uid = get_current_user_id_from_old_uerid(c.uid)
            if uid:
                c.uid = uid
                c.save()
            else:
                print c.uid
        print model, " Done!!"
    return HttpResponse("Migration Done!")
