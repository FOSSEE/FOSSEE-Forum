import os
import sys

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")

base_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

import django
django.setup()

from website.models import Question, Answer, FossCategory
from django.db.models import Count
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

class Cron(object):
    def unanswered_notification(self):
        from django.conf import settings
        import datetime as DT

        try:
            weekago = DT.date.today() - DT.timedelta(days=2)
            questions = Question.objects.filter(date_created__lte=weekago)
        except Exception, e:
            print "No questions found"
        category_count = FossCategory.objects.count()
        i = 0
        body_cat = {}
        for question in questions:
            try:
                uque = Answer.objects.filter(question__id=question.id)
            except Exception, e:
                print "error occured >> "
                print e
            if not uque.exists():
                i=i+1
                category_id = question.category.id
                if category_id in body_cat.keys():
                    body_cat[category_id].append(question)
                else:
                    body_cat[category_id] = [question]
        for key, value in body_cat.items():
            category_name = FossCategory.objects.get(id=key)
            mail_body = "Dear " + str(category_name) + " Team," + " \n\nThe following questions are left unanswered : \n\n"
            for item in value:
                string = "Question : " + str(item.title) + "\n" + str(item.category) + "\n" + settings.DOMAIN_NAME + "/question/" + str(item.id) +"\n\n"
                mail_body += string
            sender_email = settings.SENDER_EMAIL    
            mail_body += "Please do the needful.\n\nRegards,\nFOSSEE Team,\nIIT Bombay."
            to = (item.category.email,)
            subject =  "FOSSEE Forums - " + str(item.category) +" - Unanswered Question"
            send_mail(subject,mail_body, sender_email, to)


a = Cron() 
a.unanswered_notification()
