import django
import os
import sys
from builtins import str
from builtins import object
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forums.settings")

base_path =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)

django.setup()

from forums.local import FORUM_NOTIFICATION
from website.models import Question, Answer, FossCategory
from website.spamFilter import train

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
            mail_body = "<b>The following questions are left unanswered :</b><br><br>"
            for item in value:
                string = "Question : " + str(item.title) + "<br>" + str(item.category) + "<br>" + settings.DOMAIN_NAME + "/question/" + str(item.id) +"<br><br>"
                mail_body += string
            sender_email = settings.SENDER_EMAIL
            mail_body += "Please do the needful.<br><br>"
            mail_body += "<center><h6>*** This is an automatically generated email, please do not reply***</h6></center>"
            to = (item.category.email)
            bcc_email = settings.BCC_EMAIL_ID
            subject =  "FOSSEE Forums - " + str(item.category) +" - Unanswered Question"

            email = EmailMultiAlternatives(
                subject, '',
                sender_email, [to],
                bcc=[bcc_email],
                headers = {"Content-type":"text/html;charset=iso-8859-1"}
            )
            email.attach_alternative(mail_body, "text/html")
            email.content_subtype = 'html'  # Main content is text/html
            email.mixed_subtype = 'related'
            email.send(fail_silently = True)

    def train_spam_filter(self):
        train()


a = Cron()
a.unanswered_notification()
a.train_spam_filter()
