import os
import sys
import django

from website.models import Question, Answer, FossCategory
from django.db.models import Count
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

django.setup()


class Cron(object):
    def unanswered_notification(self):

        import datetime as DT

        try:
            weekago = DT.date.today() - DT.timedelta(days=7)
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
                i = i+1
                category_id = question.category.id
                if category_id in body_cat.keys():
                    body_cat[category_id].append(question)
                else:
                    body_cat[category_id] = [question]
        for key, value in body_cat.items():
            category_name = FossCategory.objects.get(id=key)
            mail_body = "Dear " + str(category_name) + " Team," +\
                        "\n\nThe following questions are left unanswered :\n\n"
            for item in value:
                string = "Question : " + str(item.title) +\
                         "\n" + str(item.category) + "\n" +\
                         "http://forums.fossee.in/question/" +\
                         str(item.id) + "\n\n"
                mail_body += string
            sender_email = "forums@fossee.in"
            mail_body += "Please do the needful.\n\nRegards,"\
                         "\nFOSSEE Team,\nIIT Bombay."
            to = (item.category.email,)
            # to = ('priyanka@fossee.in', 'rohan@fossee.in',)
            subject = "FOSSEE Forums - " + str(item.category) +\
                      " - Unanswered Question"
            send_mail(subject, mail_body, sender_email, to)

a = Cron()
a.unanswered_notification()
