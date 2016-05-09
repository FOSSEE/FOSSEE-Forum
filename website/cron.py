import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")
base_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

from website.models import Question, Answer
from django.db.models import Count
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
class Cron(object):
    def unanswered_notification(self):
        
        import datetime as DT
        try:
            weekago = DT.date.today() - DT.timedelta(days=7)
            questions = Question.objects.filter(date_created__lte=weekago)
        except Exception, e:
            print "No questions found"

        message = """ The following questions are left unanswered. Please take a look at them.: \n\n"""
        i = 0
        for question in questions:
            try:
                uque = Answer.objects.filter(question__id=question.id)
            except Exception, e:
                print "error occured >> "
                print e

            if not uque.exists():
                i=i+1
            
                message += """ 
                    Title: <b>{0}</b><br>
                    Category: <b>{1}</b><br>
                    Link: <b>{2}</b><br>
                    <hr>
                """.format(
                    question.title,
                    question.category,
                    'http://forums.fossee.in/question/' + str(question.id)
                )
        
        message+= "out of " + str(len(questions)) + " " + str(i) + " are not answered"

        sender_email = "forums@fossee.in"    
        to = ("forums@fossee.in",)
        subject = "Unanswered questions in the forums."
        if i:
            send_mail(subject,message, sender_email, to)

a = Cron()
a.unanswered_notification()