import django
import os
import sys
from builtins import str
from builtins import object
from forums.local import FORUM_NOTIFICATION
from website.models import Question, Answer, FossCategory
from django.db.models import Count
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from .spamFilter import train

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")

base_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

django.setup()

class Cron(object):

    def unanswered_notification(self):
        from django.conf import settings
        import datetime as DT

        try:
            weekago = DT.date.today() - DT.timedelta(days = 6)
            questions = Question.objects.filter(date_created__lte = weekago)
        except Exception as e:
            print("No questions found")
        category_count = FossCategory.objects.count()
        i = 0
        body_cat = {}
        for question in questions:
            try:
                uque = Answer.objects.filter(question__id = question.id)
            except Exception as e:
                print("error occured >  > ")
                print(e)
            if not uque.exists():
                i = i+1
                category_id = question.category.id
                if category_id in list(body_cat.keys()):
                    body_cat[category_id].append(question)
                else:
                    body_cat[category_id] = [question]
        for key, value in list(body_cat.items()):
            category_name = FossCategory.objects.get(id = key)
            mail_body = "*** This is an automatically generated email, please do not reply ***" + " \n\nThe following questions are left unanswered : \n\n"
            for item in value:
                string = "Question : " + str(item.title) + "\n" + str(item.category) + "\n" + settings.DOMAIN_NAME + "/question/" + str(item.id) +"\n\n"
                mail_body += string
            sender_email = settings.SENDER_EMAIL
            mail_body += "Please do the needful.\n\n"
            to = (item.category.email, FORUM_NOTIFICATION)
            subject =  "FOSSEE Forums - " + str(item.category) +" - Unanswered Question"
            send_mail(subject, mail_body, sender_email, to)

    def train_spam_filter(self):
        train()


a = Cron()
a.unanswered_notification()
a.train_spam_filter()
