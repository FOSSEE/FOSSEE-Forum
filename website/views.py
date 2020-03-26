from builtins import zip
from builtins import str
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from django.utils.html import strip_tags
from website.models import *
from website.forms import NewQuestionForm, AnswerQuestionForm, AnswerCommentForm
from website.templatetags.helpers import prettify
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from .spamFilter import predict, train
from .decorators import check_recaptcha
from django.urls import resolve, Resolver404
from .auto_mail_send import *
from datetime import date, datetime
import openpyxl

User = get_user_model()
admins = (
    9, 4376, 4915, 14595, 12329, 22467, 5518, 30705
)

# Function to check if user is in any moderator group or to check whether user belongs to the moderator group of question's category



def is_moderator(user, question=None):
    if question:
        return user.groups.filter(moderatorgroup=ModeratorGroup.objects.get(category=question.category)).exists()
    return user.groups.count() > 0

# Function to check if user is anonymous, and if not he/she has first_name
# and last_name


def account_credentials_defined(user):
    return ((user.first_name and user.last_name) or is_moderator(user))

# for home page


def home(request):
    send_remider_mail()
    settings.MODERATOR_ACTIVATED = False
    next = request.GET.get('next', '')
    next = next.split('/')
    if 'moderator' in next:
        next.remove('moderator')
    next = '/'.join(next)
    try:
        resolve(next)
        return HttpResponseRedirect(next)
    except Resolver404:
        if next:
            return HttpResponseRedirect('/')
    categories = FossCategory.objects.order_by('name')
    questions = Question.objects.filter(
        is_spam=False, is_active=True).order_by('-date_created')
    context = {
        'categories': categories,
        'questions': questions,
    }
    return render(request, "website/templates/index.html", context)

# to get all questions posted till now and pagination, 20 questions at a time


def questions(request):
    if is_moderator(request.user) and settings.MODERATOR_ACTIVATED:
        return HttpResponseRedirect('/moderator/questions/')
    categories = FossCategory.objects.order_by('name')
    questions = Question.objects.all().filter(
        is_spam=False, is_active=True).order_by('-date_created')
    context = {
        'categories': categories,
        'questions': questions,
    }
    return render(request, 'website/templates/questions.html', context)

# get particular question, with votes,anwsers


def get_question(request, question_id=None, pretty_url=None):
    if is_moderator(request.user,get_object_or_404(Question, id=question_id)) and settings.MODERATOR_ACTIVATED:
        question = get_object_or_404(Question, id=question_id)
        answers = question.answer_set.all()
    elif is_moderator(request.user) and settings.MODERATOR_ACTIVATED:
        return HttpResponseRedirect("/moderator/")
    else:
        question = get_object_or_404(Question, id=question_id, is_active=True)
        answers = question.answer_set.filter(
                 is_active=True).all()
    sub_category = True

    if question.sub_category == "" or str(question.sub_category) == 'None':
        sub_category = False

    ans_count = len(answers)
    form = AnswerQuestionForm()
    thisuserupvote = question.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = question.userDownVotes.filter(
        id=request.user.id).count()

    ans_votes = []
    for vote in answers:
        net_ans_count = vote.num_votes
        ans_votes.append([vote.userUpVotes.filter(id=request.user.id).count(
        ), vote.userDownVotes.filter(id=request.user.id).count(), net_ans_count])

    main_list = list(zip(answers, ans_votes))
    context = {
        'ans_count': ans_count,
        'question': question,
        'sub_category': sub_category,
        'main_list': main_list,
        'form': form,
        'thisUserUpvote': thisuserupvote,
        'thisUserDownvote': thisuserdownvote,
        'net_count': question.num_votes,
    }
    context.update(csrf(request))

    # updating views count
    if (request.user.is_anonymous):  # if no one logged in
        question.views += 1
    elif (question.userViews.filter(id=request.user.id).count() == 0):
        question.views += 1
        question.userViews.add(request.user)

    question.save()

    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    return render(request, 'website/templates/get-question.html', context)

def to_uids(question):
    answers = Answer.objects.filter(
        question_id=question.id, is_active=True).distinct()
    mail_uids = [question.user.id]
    for answer in answers:
        for comment in AnswerComment.objects.values('uid').filter(answer=answer, is_active=True).distinct():
            mail_uids.append(comment['uid'])
        mail_uids.append(answer.uid)
    mail_uids = set(mail_uids)
    return mail_uids

def send_email(sender_email, to, subject, message, bcc_email=None):
    email = EmailMultiAlternatives(
        subject, '',
        sender_email, to,
        bcc=[bcc_email],
        headers={"Content-type": "text/html;charset=iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    email.content_subtype = 'html'  # Main content is text/html
    email.mixed_subtype = 'related'
    email.send(fail_silently=True)

# post answer to a question, send notification to the user, whose question is answered
# if anwser is posted by the owner of the question, no notification is sent
@login_required
@check_recaptcha
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def question_answer(request, question_id):

    question = get_object_or_404(Question, id=question_id, is_active=True)
    if (request.method == 'POST'):

        form = AnswerQuestionForm(request.POST, request.FILES)
        answer = Answer()
        answer.uid = request.user.id

        if form.is_valid() and request.recaptcha_is_valid:
            cleaned_data = form.cleaned_data
            body = cleaned_data['body']
            answer.body = body.splitlines()
            answer.question = question
            answer.body = body
            if ('image' in request.FILES):
                answer.image = request.FILES['image']
            if (predict(answer.body) == "Spam"):
                answer.is_spam = True
            answer.save()

            # if user_id of question does not match to user_id of answer, send
            # notification
            if ((question.user.id != request.user.id)
                    and (answer.is_spam == False)):
                notification = Notification()
                notification.uid = question.user.id
                notification.qid = question.id
                notification.aid = answer.id
                notification.save()

                # Sending email when a new answer is posted
                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                bcc_email = settings.BCC_EMAIL_ID
                subject = "FOSSEE Forums - {0} - Your question has been answered".format(
                    question.category)
                to = [question.user.email]
                message = """The following new answer has been posted in the FOSSEE Forum: <br><br>
                    <b>Title:</b> {0} <br>
                    <b>Category:</b> {1}<br>
                    <b>Link:</b> {2}<br><br>

                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    question.title,
                    question.category,
                    settings.DOMAIN_NAME + '/question/' + str(question_id) + "#answer" + str(answer.id)
                )
                send_email(sender_email, to, subject, message, bcc_email)

            mail_uids = to_uids(question)
            mail_uids.difference_update({question.user.id, request.user.id})

            # Notification for all user in this thread
            for mail_uid in mail_uids:

                notification = Notification()
                notification.uid = mail_uid
                notification.qid = question.id
                notification.aid = answer.id
                notification.save()

                # Sending email to thread when a new answer is posted
                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                bcc_email = settings.BCC_EMAIL_ID
                subject = "FOSSEE Forums - {0} - Question has been answered".format(
                    question.category)
                to = [get_user_email(mail_uid)]
                message = """The following new answer has been posted in the FOSSEE Forum: <br><br>
                    <b>Title:</b> {0} <br>
                    <b>Category:</b> {1}<br>
                    <b>Link:</b> {2}<br><br>

                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    question.title,
                    question.category,
                    settings.DOMAIN_NAME + '/question/' + str(question_id) + "#answer" + str(answer.id)
                )
                send_email(sender_email, to, subject, message, bcc_email)

            return HttpResponseRedirect('/question/{0}/'.format(question_id))

        else:
            messages.error(request,"Answer cann't be empty or only blank spaces.")
    return HttpResponseRedirect('/question/{0}/'.format(question_id))


# comments for specific answer and notification is sent to owner of the answer
# notify other users in the comment thread
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def answer_comment(request):

    if (request.method == 'POST'):

        answer_id = request.POST['answer_id']
        answer = Answer.objects.get(pk=answer_id, is_active=True)
        answers = answer.question.answer_set.filter(
            is_spam=False, is_active=True).all()
        answer_creator = answer.user()
        form = AnswerCommentForm(request.POST)

        if form.is_valid():

            body = request.POST['body']
            comment = AnswerComment()
            comment.uid = request.user.id
            comment.answer = answer
            comment.body = body
            comment.save()

            # notifying the answer owner
            if answer.uid != request.user.id:
                notification = Notification()
                notification.uid = answer.uid
                notification.qid = answer.question.id
                notification.aid = answer.id
                notification.cid = comment.id
                notification.save()

                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                bcc_email = settings.BCC_EMAIL_ID
                subject = "FOSSEE Forums - {0} - Comment for your answer".format(
                    answer.question.category)
                to = [answer_creator.email]
                message = """
                    A comment has been posted on your answer. <br><br>
                    <b>Title:</b> {0}<br>
                    <b>Category:</b> {1}<br>
                    <b>Link:</b> {2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    answer.question.title,
                    answer.question.category,
                    settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
                )
                send_email(sender_email, to, subject, message, bcc_email)

            comment_creator = AnswerComment.objects.order_by('-date_created').values(
                'uid').filter(answer=answer, is_active=True).exclude(uid=request.user.id).distinct()
            if comment_creator:

                notification = Notification()
                notification.uid = comment_creator[0]['uid']
                notification.qid = answer.question.id
                notification.aid = answer.id
                notification.cid = comment.id
                notification.save()

                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                bcc_email = settings.BCC_EMAIL_ID
                subject = "FOSSEE Forums - {0} - Comment has a reply".format(
                    answer.question.category)
                to = [get_user_email(comment_creator[0]['uid'])]
                message = """
                    A reply has been posted on your comment.<br><br>
                    <b>Title:</b> {0}<br>
                    <b>Category:</b> {1}<br>
                    <b>Link:</b> {2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    answer.question.title,
                    answer.question.category,
                    settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
                )

                send_email(sender_email, to, subject, message, bcc_email)

            mail_uids = to_uids(answer.question)
            mail_uids.difference_update({answer.uid, comment_creator, request.user.id})

            for mail_uid in mail_uids:

                notification = Notification()
                notification.uid = mail_uid
                notification.qid = answer.question.id
                notification.aid = answer.id
                notification.cid = comment.id
                notification.save()

                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                bcc_email = settings.BCC_EMAIL_ID
                subject = "FOSSEE Forums - A Comment has been posted under Question No. {0}".format(
                    answer.question.id)
                to = [get_user_email(mail_uid)]
                message = """
                    A comment has been posted under the Question.<br><br>
                    <b>Title:</b> {0}<br>
                    <b>Category:</b> {1}<br>
                    <b>Link:</b> {2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    answer.question.title,
                    answer.question.category,
                    settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
                )

                send_email(sender_email, to, subject, message, bcc_email)

            return HttpResponseRedirect(
                '/question/{0}/'.format(answer.question.id))

        else:
            messages.error(request,"Comment cann't be empty or only blank spaces.")
            return HttpResponseRedirect(
                '/question/{0}/'.format(answer.question.id))
    else:
        return render(request, 'website/templates/404.html')

# View used to filter question according to category


def filter(request, category=None, tutorial=None):

    if category and tutorial:
        questions = Question.objects.filter(
            category__name=category).filter(
            sub_category=tutorial).order_by('-date_created')
    elif tutorial is None:
        questions = Question.objects.filter(
            category__name=category).order_by('-date_created')

    if (not settings.MODERATOR_ACTIVATED):
        questions = questions.filter(is_spam=False, is_active=True)

    context = {
        'questions': questions,
        'category': category,
        'tutorial': tutorial,
    }

    return render(request, 'website/templates/filter.html', context)

# post a new question on to forums, notification is sent to mailing list
# team@fossee.in
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def new_question(request):

    if settings.MODERATOR_ACTIVATED:
        return HttpResponseRedirect('/moderator/')

    # settings.MODERATOR_ACTIVATED = False

    context = {}
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    all_category = FossCategory.objects.all()

    if (request.method == 'POST'):

        form = NewQuestionForm(request.POST, request.FILES)

        if form.is_valid():

            cleaned_data = form.cleaned_data
            question = Question()
            question.user = request.user
            question.category = cleaned_data['category']
            question.sub_category = cleaned_data['tutorial']

            if ('image' in request.FILES):
                question.image = request.FILES['image']

            if (question.sub_category == "Select a Sub Category"):

                if (str(question.category) == "Scilab Toolbox"):
                    context.update(csrf(request))
                    category = request.POST.get('category', None)
                    context['category'] = category
                    context['form'] = NewQuestionForm(category=category)
                    return render(
                        request, 'website/templates/new-question.html', context)

                question.sub_category = ""

            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.views = 1
            question.save()
            question.userViews.add(request.user)
            if (str(question.sub_category) == 'None'):
                question.sub_category = ""
            if (predict(question.body) == "Spam"):
                question.is_spam = True

            question.save()

            # Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(
                question.category)
            to = [question.category.email]
            message = """
                The following new question has been posted in the FOSSEE Forum: <br>
                <b> Title: </b>{0}<br>
                <b> Category: </b>{1}<br>
                <b> Link: </b><a href="{3}">{3}</a><br>
                <b> Question : </b>{2}<br><br>
                Regards,<br>
                FOSSEE Team,<br>
                FOSSEE, IIT Bombay
                <br><br><br>
                <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                """.format(
                question.title,
                question.category,
                question.body,
                settings.DOMAIN_NAME + '/question/' + str(question.id),
            )
            send_email(sender_email, to, subject, message)
            to = [settings.BCC_EMAIL_ID]
            message = """
                The following new question has been posted in the FOSSEE Forum: <br>
                <b> Title: </b>{0}<br>
                <b> Category: </b>{1}<br>
                <b> Link: </b><a href="{3}">{3}</a><br>
                <b> Question : </b>{2}<br>
                <b> Classified as spam: </b>{4}<br><br>
                Regards,<br>
                FOSSEE Team,<br>
                FOSSEE, IIT Bombay
                <br><br><br>
                <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                """.format(
                question.title,
                question.category,
                question.body,
                settings.DOMAIN_NAME + '/question/' + str(question.id),
                question.is_spam,
            )
            send_email(sender_email, to, subject, message)

            if (question.is_spam):
                return HttpResponseRedirect('/')
            return HttpResponseRedirect('/question/{0}/'.format(question.id))

        else:
            context.update(csrf(request))
            category = request.POST.get('category', None)
            tutorial = request.POST.get('tutorial', None)
            context['category'] = category
            context['tutorial'] = tutorial
            context['form'] = form
            return render(
                request,
                'website/templates/new-question.html',
                context)

    else:
        category = request.GET.get('category')
        form = NewQuestionForm(category=category)
        context['category'] = category

    context['form'] = form
    context.update(csrf(request))
    return render(request, 'website/templates/new-question.html', context)

# Edit a question on forums, notification is sent to mailing list
# team@fossee.in
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def edit_question(request, question_id):

    context = {}
    user = request.user
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    all_category = FossCategory.objects.all()
    question = get_object_or_404(Question, id=question_id, is_active=True)

    # To prevent random user from manually entering the link and editing
    if ((request.user.id != question.user.id or question.answer_set.filter(is_active=True).count(
    ) > 0) and (not is_moderator(request.user, question) or not settings.MODERATOR_ACTIVATED)):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == 'POST'):

        previous_title = question.title
        form = NewQuestionForm(request.POST, request.FILES)
        question.title = ''  # To prevent same title error in form
        question.save()

        if form.is_valid():

            cleaned_data = form.cleaned_data
            question.category = cleaned_data['category']
            question.sub_category = cleaned_data['tutorial']

            if ('image' in request.FILES):
                question.image = request.FILES['image']

            if (question.sub_category == "Select a Sub Category"):
                if (str(question.category) == "Scilab Toolbox"):
                    context.update(csrf(request))
                    category = request.POST.get('category', None)
                    tutorial = request.POST.get('tutorial', None)
                    context['category'] = category
                    context['tutorial'] = tutorial
                    context['form'] = form
                    return render(
                        request, 'website/templates/edit-question.html', context)

                question.sub_category = ""

            change_spam = question.is_spam

            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.is_spam = cleaned_data['is_spam']

            if question.is_spam != change_spam:
                add_Spam(question.body, question.is_spam)

            question.views = 1
            question.save()
            question.userViews.add(request.user)
            if str(question.sub_category) == 'None':
                question.sub_category = ""
            if (not settings.MODERATOR_ACTIVATED):
                if (predict(question.body) == "Spam"):
                    question.is_spam = True

            question.save()
            
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(
                question.category)
            bcc_email = (
                question.category.email,
                settings.FORUM_NOTIFICATION)
            message = """
                The following question has been edited in the FOSSEE Forum: <br>
                <b> Original title: </b>{0}<br>
                <b> New title: </b>{1}<br>
                <b> Category: </b>{2}<br>
                <b> Link: </b><a href="{4}">{4}</a><br>
                <b> Question : </b>{3}<br><br>
                Regards,<br>
                FOSSEE Team,<br>
                FOSSEE, IIT Bombay
                <br><br><br>
                <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                """.format(
                question.title,
                previous_title,
                question.category,
                question.body,
                settings.DOMAIN_NAME + '/question/' + str(question.id),
            )
            mail_uids = to_uids(question)
            for uid in mail_uids:
                to = [get_user_email(uid)]
                send_email(sender_email, to, subject, message, bcc_email)

            if (question.is_spam and not settings.MODERATOR_ACTIVATED):
                return HttpResponseRedirect('/')

            return HttpResponseRedirect('/question/{0}/'.format(question.id))

        else:

            context.update(csrf(request))
            category = request.POST.get('category', None)
            tutorial = request.POST.get('tutorial', None)
            context['category'] = category
            context['tutorial'] = tutorial
            context['form'] = form
            return render(
                request,
                'website/templates/edit-question.html',
                context)

    else:
        form = NewQuestionForm(instance=question)

    context['form'] = form
    context.update(csrf(request))
    return render(request, 'website/templates/edit-question.html', context)


def add_Spam(question_body, is_spam):
    xfile = openpyxl.load_workbook(settings.BASE_DIR + '/Spam_Filter_Data/DataSet.xlsx')
    sheet = xfile['Data set']
    n = len(sheet['A']) + 1
    for i in range(2, n):
        if(question_body == str(sheet.cell(row=i, column=1).value)):
            sheet.cell(row=i, column=2).value = is_spam
            xfile.save('DataSet.xlsx')
            return
    sheet['A%s' % n] = question_body
    sheet['B%s' % n] = is_spam
    xfile.save('DataSet.xlsx')

# View for deleting question, notification is sent to mailing list
# team@fossee.in
@login_required
def question_delete(request, question_id):

    question = get_object_or_404(Question, id=question_id, is_active=True)
    title = question.title

    # To prevent random user from manually entering the link and deleting
    if ((request.user.id != question.user.id or question.answer_set.filter(
            is_active=True).count() > 0) and (not is_moderator(request.user, question) or not settings.MODERATOR_ACTIVATED)):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == "POST"):

        # Send a delete email only when moderator does so
        if (settings.MODERATOR_ACTIVATED):
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(
                question.category)
            bcc_email = settings.BCC_EMAIL_ID
            delete_reason = request.POST.get('deleteQuestion')
            message = """
                The following question has been deleted by a moderator of the FOSSEE Forum: <br>
                <b> Title: </b>{0}<br>
                <b> Category: </b>{1}<br>
                <b> Question: </b>{2}<br>
                <b> Moderator comments: </b>{3}<br><br>
                Regards,<br>
                FOSSEE Team,<br>
                FOSSEE, IIT Bombay
                <br><br><br>
                <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                """.format(
                title,
                question.category,
                question.body,
                delete_reason,
            )
            mail_uids = to_uids(question)
            for uid in mail_uids:
                to = [get_user_email(uid)]
                send_email(sender_email, to, subject, message, bcc_email)

    question.is_active = False
    question.save()
    answers = question.answer_set.all()
    for answer in answers:
        answer.is_active = False
        answer.save()
        for comment in answer.answercomment_set.all():
            comment.is_active = False
            comment.save()
    return render(request,
                  'website/templates/question-delete.html',
                  {'title': title})


@login_required
def question_restore(request, question_id):
    question = get_object_or_404(Question, id=question_id, is_active=False)
    if not is_moderator(request.user, question) or not settings.MODERATOR_ACTIVATED:
        return render(request, 'website/templates/not-authorized.html')
    question.is_active = True
    question.save()
    for answer in question.answer_set.all():
        answer.is_active = True
        answer.save()
        for comment in answer.answercomment_set.all():
            comment.is_active = True
            comment.save()
    return HttpResponseRedirect('/question/{0}/'.format(question_id))

# View for deleting answer, notification is sent to person who posted answer
# @user_passes_test(is_moderator)
@login_required
def answer_delete(request, answer_id):

    answer = get_object_or_404(Answer, id=answer_id)
    question_id = answer.question.id

    if ((request.user.id != answer.uid or AnswerComment.objects.filter(answer=answer,
                                                                       is_active=True).exclude(uid=answer.uid).exists()) and (not is_moderator(request.user, answer.question) or not settings.MODERATOR_ACTIVATED)):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == "POST") and (settings.MODERATOR_ACTIVATED):

        # Sending email to user when answer is deleted
        sender_name = "FOSSEE Forums"
        sender_email = settings.SENDER_EMAIL
        subject = "FOSSEE Forums - {0} - Answer Deleted".format(
            answer.question.category)
        bcc_email = settings.BCC_EMAIL_ID
        delete_reason = request.POST.get('deleteAnswer')
        message = """
            The following answer has been deleted by a moderator in the FOSSEE Forum: <br>
            <b> Answer: </b>{0}<br>
            <b> Category: </b>{1}<br>
            <b> Question: </b>{2}<br>
            <b> Moderator comments: </b>{3}<br><br>
            Regards,<br>
            FOSSEE Team,<br>
            FOSSEE, IIT Bombay
            <br><br><br>
            <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
            """.format(
            answer.body,
            answer.question.category,
            answer.question.body,
            delete_reason,
        )
        mail_uids = to_uids(answer.question)
        for uid in mail_uids:
            to = [get_user_email(uid)]
            send_email(sender_email, to, subject, message, bcc_email)

        answer.is_active = False
        answer.save()
        for comment in answer.answercomment_set.all():
            comment.is_active = False
            comment.save()
    return HttpResponseRedirect('/question/{0}/'.format(question_id))


@login_required
@user_passes_test(is_moderator)
def answer_restore(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id, is_active=False)
    if not is_moderator(request.user, answer.question) or not settings.MODERATOR_ACTIVATED:
        return render(request, 'website/templates/not-authorized.html')
    if not answer.question.is_active:
        messages.error(
            request,
            "Answer can only be restored when its question is not deleted.")
        return HttpResponseRedirect(
            '/question/{0}/'.format(answer.question.id))
    answer.is_active = True
    answer.save()
    for comment in answer.answercomment_set.all():
        comment.is_active = True
        comment.save()
    return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))

@login_required
@user_passes_test(is_moderator)
def comment_restore(request, comment_id):
    comment = get_object_or_404(AnswerComment, id=comment_id, is_active=False)
    if not settings.MODERATOR_ACTIVATED:
        return render(request, 'website/templates/not-authorized.html')
    if not comment.answer.is_active:
        messages.error(
            request,
            "Comment can only be restored when its answer is not deleted")
        return HttpResponseRedirect(
            '/question/{0}/'.format(comment.answer.question.id))
    comment.is_active = True
    comment.save()
    return HttpResponseRedirect(
        '/question/{0}/'.format(comment.answer.question.id))

# View to mark answer as spam/non-spam
@login_required
@user_passes_test(is_moderator)
def mark_answer_spam(request, answer_id):

    answer = get_object_or_404(Answer, id=answer_id, is_active=True)
    question_id = answer.question.id

    if (request.method == "POST"):
        type = request.POST['selector']
        if (type == "spam"):
            answer.is_spam = True
        else:
            answer.is_spam = False
    answer.save()
    return HttpResponseRedirect(
        '/question/{0}/#answer{1}/'.format(question_id, answer.id))

# return number of votes and initial votes
# user who asked the question,cannot vote his/or anwser,
# other users can post votes
@login_required
def vote_post(request):

    post_id = int(request.POST.get('id'))
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    cur_post = get_object_or_404(Question, id=post_id, is_active=True)
    thisuserupvote = cur_post.userUpVotes.filter(
        id=request.user.id, is_active=True).count()
    thisuserdownvote = cur_post.userDownVotes.filter(
        id=request.user.id, is_active=True).count()
    initial_votes = cur_post.num_votes

    if (request.user.id != cur_post.user.id):

        # This condition is for adding vote
        if vote_action == 'vote':
            if (thisuserupvote == 0) and (thisuserdownvote == 0):
                if vote_type == 'up':
                    cur_post.userUpVotes.add(request.user)
                elif vote_type == 'down':
                    cur_post.userDownVotes.add(request.user)
                else:
                    return HttpResponse(initial_votes)
            else:
                if (thisuserupvote == 1) and (vote_type == 'down'):
                    cur_post.userUpVotes.remove(request.user)
                    cur_post.userDownVotes.add(request.user)
                elif (thisuserdownvote == 1) and (vote_type == 'up'):
                    cur_post.userDownVotes.remove(request.user)
                    cur_post.userUpVotes.add(request.user)
                else:
                    return HttpResponse(initial_votes)

        # This condition is for canceling vote
        elif vote_action == 'recall-vote':
            if (vote_type == 'up') and (thisuserupvote == 1):
                cur_post.userUpVotes.remove(request.user)
            elif (vote_type == 'down') and (thisuserdownvote == 1):
                cur_post.userDownVotes.remove(request.user)
            else:
                return HttpResponse(initial_votes)
        else:
            return HttpResponse("Error: Bad Action.")

        num_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()
        cur_post.num_votes = num_votes
        cur_post.save()
        return HttpResponse(num_votes)

    else:
        return HttpResponse(initial_votes)

# return number of votes and initial votes
# user who posted the answer, cannot vote his/or anwser,
# other users can post votes
@login_required
def ans_vote_post(request):

    post_id = int(request.POST.get('id'))
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    cur_post = get_object_or_404(Answer, id=post_id, is_active=True)
    thisuserupvote = cur_post.userUpVotes.filter(
        id=request.user.id, is_active=True).count()
    thisuserdownvote = cur_post.userDownVotes.filter(
        id=request.user.id, is_active=True).count()
    initial_votes = cur_post.num_votes

    if (request.user.id != cur_post.uid):

        # This condition is for voting
        if (vote_action == 'vote'):
            if (thisuserupvote == 0) and (thisuserdownvote == 0):
                if vote_type == 'up':
                    cur_post.userUpVotes.add(request.user)
                elif vote_type == 'down':
                    cur_post.userDownVotes.add(request.user)
                else:
                    return HttpResponse(initial_votes)
            else:
                if (thisuserupvote == 1) and (vote_type == 'down'):
                    cur_post.userUpVotes.remove(request.user)
                    cur_post.userDownVotes.add(request.user)
                elif (thisuserdownvote == 1) and (vote_type == 'up'):
                    cur_post.userDownVotes.remove(request.user)
                    cur_post.userUpVotes.add(request.user)
                else:
                    return HttpResponse(initial_votes)

        # This condition is for canceling vote
        elif (vote_action == 'recall-vote'):
            if (vote_type == 'up') and (thisuserupvote == 1):
                cur_post.userUpVotes.remove(request.user)
            elif (vote_type == 'down') and (thisuserdownvote == 1):
                cur_post.userDownVotes.remove(request.user)
            else:
                return HttpResponse(initial_votes)
        else:
            return HttpResponse(initial_votes)

        num_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()
        cur_post.num_votes = num_votes
        cur_post.save()
        return HttpResponse(num_votes)

    else:
        return HttpResponse(initial_votes)


# notification if any on header, when user logs in to the account
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def user_notifications(request, user_id):

    if settings.MODERATOR_ACTIVATED:
        return HttpResponseRedirect('/moderator/')

    # settings.MODERATOR_ACTIVATED = False

    if (user_id == request.user.id):
        try:
            notifications = Notification.objects.filter(
                uid=user_id).order_by('-date_created')
            context = {
                'notifications': notifications,
            }
            return render(
                request,
                'website/templates/notifications.html',
                context)
        except BaseException:
            return HttpResponseRedirect(
                "/user/{0}/notifications/".format(request.user.id))

    else:
        return render(request, 'website/templates/not-authorized.html')


# to clear notification from header, once viewed or cancelled
@login_required
def clear_notifications(request):
    settings.MODERATOR_ACTIVATED = False
    Notification.objects.filter(uid=request.user.id).delete()
    return HttpResponseRedirect(
        "/user/{0}/notifications/".format(request.user.id))


def search(request):
    if settings.MODERATOR_ACTIVATED:
        return HttpResponseRedirect('/moderator/')
    categories = FossCategory.objects.order_by('name')
    context = {
        'categories': categories
    }

    return render(request, 'website/templates/search.html', context)


# MODERATOR SECTION
# All the moderator views go below

# Moderator panel home page
@login_required
@user_passes_test(is_moderator)
def moderator_home(request):

    settings.MODERATOR_ACTIVATED = True
    next = request.GET.get('next', '')
    if next == '/':
        return HttpResponseRedirect('/moderator/')
    try:
        resolve(next)
        return HttpResponseRedirect(next)
    except Resolver404:
        if next:
            return HttpResponseRedirect('/moderator/')
    # If user is a master moderator
    if (request.user.groups.filter(name="forum_moderator").exists()):
        questions = Question.objects.filter().order_by('-date_created')
        categories = FossCategory.objects.order_by('name')

    else:
        # Finding the moderator's categories and Getting the questions related
        # to moderator's categories
        categories = []
        questions = []
        for group in request.user.groups.all():
            category = ModeratorGroup.objects.get(group=group).category
            categories.append(category)
            questions.extend(
                Question.objects.filter(
                    category__name=category.name).order_by('-date_created'))
        questions.sort(
            key=lambda question: question.date_created,
            reverse=True)
    context = {
        'questions': questions,
        'categories': categories,
    }

    return render(request, 'website/templates/moderator/index.html', context)

# All questions page for moderator
@login_required
@user_passes_test(is_moderator)
def moderator_questions(request):

    # If user is a master moderator
    if (request.user.groups.filter(name="forum_moderator").exists()):
        categories = FossCategory.objects.order_by('name')
        questions = Question.objects.filter().order_by('-date_created')
        if ('spam' in request.GET):
            questions = questions.filter(is_spam=True)
        elif ('non-spam' in request.GET):
            questions = questions.filter(is_spam=False)

    else:
        # Finding the moderator's category questions
        questions = []
        categories = []
        for group in request.user.groups.all():
            category = ModeratorGroup.objects.get(group=group).category
            categories.append(category)
            questions_to_add = Question.objects.filter(
                category__name=category.name).order_by('-date_created')
            if ('spam' in request.GET):
                questions_to_add = questions_to_add.filter(is_spam=True)
            elif ('non-spam' in request.GET):
                questions_to_add = questions_to_add.filter(is_spam=False)
            questions.extend(questions_to_add)
        questions.sort(
            key=lambda question: question.date_created,
            reverse=True)
    context = {
        'categories': categories,
        'questions': questions,
    }

    return render(
        request,
        'website/templates/moderator/questions.html',
        context)

# Unanswered questions page for moderator
@login_required
@user_passes_test(is_moderator)
def moderator_unanswered(request):

    settings.MODERATOR_ACTIVATED = True
    # If user is a master moderator
    if (request.user.groups.filter(name="forum_moderator").exists()):
        categories = FossCategory.objects.order_by('name')
        questions = Question.objects.all().filter(
            is_active=True).order_by('date_created').reverse()

    else:
        # Finding the moderator's category questions
        questions = []
        categories = []
        for group in request.user.groups.all():
            category = ModeratorGroup.objects.get(group=group).category
            categories.append(category)
            questions.extend(
                Question.objects.filter(
                    category__name=category.name,
                    is_active=True).order_by('-date_created'))
        questions.sort(
            key=lambda question: question.date_created,
            reverse=True)
    context = {
        'categories': categories,
        'questions': questions,
    }

    return render(
        request,
        'website/templates/moderator/unanswered.html',
        context)

# Re-training spam filter
@login_required
@user_passes_test(is_moderator)
def train_spam_filter(request):

    next = request.GET.get('next', '')
    train()
    try:
        resolve(next)
        return HttpResponseRedirect(next)
    except Resolver404:
        return HttpResponseRedirect('/moderator/')

# AJAX SECTION
# All the ajax views go below
@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':

        category = request.POST.get('category')

        if (SubFossCategory.objects.filter(parent_id=category).exists()):
            tutorials = SubFossCategory.objects.filter(parent_id=category)
            context = {
                'tutorials': tutorials,
            }
            return render(
                request,
                'website/templates/ajax-tutorials.html',
                context)

        else:
            return HttpResponse('No sub-category in category.')

    else:
        return render(request, 'website/templates/404.html')


def ajax_answer_update(request):

    if request.method == 'POST':
        aid = request.POST['answer_id']
        body = request.POST['answer_body']
        answer = get_object_or_404(Answer, pk=aid, is_active=True)
        if ((is_moderator(request.user, answer.question) and settings.MODERATOR_ACTIVATED) or (request.user.id ==
                                                                              answer.uid and not AnswerComment.objects.filter(answer=answer).exclude(uid=answer.uid).exists())):
            answer.body = str(body)
            answer.save()
            if settings.MODERATOR_ACTIVATED:
                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                subject = "FOSSEE Forums - {0} - Answer Deleted".format(
                    answer.question.category)
                bcc_email = settings.BCC_EMAIL_ID
                delete_reason = request.POST.get('deleteAnswer')
                message = """
                    The following answer has been edited by a moderator in the FOSSEE Forum: <br>
                    <b> Answer: </b>{0}<br>
                    <b> Category: </b>{1}<br>
                    <b> Question: </b>{2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    answer.body,
                    answer.question.category,
                    answer.question.body,
                )
                mail_uids = to_uids(answer.question)
                for uid in mail_uids:
                    to = [get_user_email(uid)]
                    send_email(sender_email, to, subject, message, bcc_email)
            messages.success(request, "Answer is Successfully Saved")
            return HttpResponseRedirect(
                '/question/{0}/'.format(answer.question.id))
        else:
            messages.error(request, "Only moderator can update.")
            return HttpResponseRedirect(
                '/question/{0}/'.format(answer.question.id))
    else:
        return render(request, 'website/templates/404.html')


@csrf_exempt
def ajax_answer_comment_delete(request):
    if request.method == 'POST':
        comment_id = request.POST['comment_id']
        comment = get_object_or_404(AnswerComment, pk=comment_id)
        if (is_moderator(request.user, comment.answer.question) and settings.MODERATOR_ACTIVATED) or (
                request.user.id == comment.uid and can_delete(comment.answer, comment_id)):
            comment.is_active = False
            comment.save()
            if settings.MODERATOR_ACTIVATED:

                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                subject = "FOSSEE Forums - {0} - Comment Deleted".format(
                    comment.answer.question.category)
                bcc_email = settings.BCC_EMAIL_ID
                # delete_reason = request.POST.get('deleteAnswer')
                message = """
                    The following comment has been deleted by a moderator in the FOSSEE Forum: <br>
                    <b> Comment: </b>{0}<br>
                    <b> Category: </b>{1}<br>
                    <b> Answer: </b>{2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    comment.body,
                    comment.answer.question.category,
                    comment.answer.body,
                )
                mail_uids = to_uids(comment.answer.question)
                for uid in mail_uids:
                    to = [get_user_email(uid)]
                    send_email(sender_email, to, subject, message, bcc_email)
            return HttpResponse('deleted')
        else:
            messages.error(request, "Only Moderator can delete.")
            return HttpResponseRedirect(
                '/question/{0}/'.format(comment.answer.question.id))
    else:
        return render(request, 'website/templates/404.html')


@csrf_exempt
def ajax_answer_comment_update(request):
    if request.method == 'POST':
        cid = request.POST['comment_id']
        body = request.POST['comment_body']
        comment = get_object_or_404(AnswerComment, pk=cid, is_active=True)
        if (is_moderator(request.user, comment.answer.question) and settings.MODERATOR_ACTIVATED) or (
                request.user.id == comment.uid and can_delete(comment.answer, cid)):
            comment.body = str(body)
            comment.save()
            if settings.MODERATOR_ACTIVATED:
                sender_name = "FOSSEE Forums"
                sender_email = settings.SENDER_EMAIL
                subject = "FOSSEE Forums - {0} - Answer Deleted".format(
                    comment.answer.question.category)
                bcc_email = settings.BCC_EMAIL_ID
                message = """
                    The following comment has been edited by a moderator in the FOSSEE Forum: <br>
                    <b> Comment: </b>{0}<br>
                    <b> Category: </b>{1}<br>
                    <b> Question: </b>{2}<br><br>
                    Regards,<br>
                    FOSSEE Team,<br>
                    FOSSEE, IIT Bombay
                    <br><br><br>
                    <center><h6>*** This is an automatically generated email, please do not reply***</h6></center>
                    """.format(
                    comment.body,
                    comment.answer.question.category,
                    comment.answer.question.body,
                )
                mail_uids = to_uids(comment.answer.question)
                mail_uids.discard(request.user.id)
                for uid in mail_uids:
                    to = [get_user_email(uid)]
                    send_email(sender_email, to, subject, message, bcc_email)
            messages.success(request, "Comment is Successfully Saved")
            return HttpResponseRedirect(
                '/question/{0}/'.format(comment.answer.question.id))
        else:
            messages.error(request, "Only moderator can update.")
            return HttpResponseRedirect(
                '/question/{0}/'.format(comment.answer.question.id))
    else:
        return render(request, 'website/templates/404.html')


def can_delete(answer, comment_id):
    comments = answer.answercomment_set.filter(is_active=True).all()
    for c in comments:
        if c.id > int(comment_id):
            return False
    return True


@csrf_exempt
def ajax_notification_remove(request):
    if request.method == "POST":

        nid = request.POST["notification_id"]

        try:
            notification = get_object_or_404(Notification, pk=nid)
            if (notification.uid == request.user.id):
                notification.delete()
                return HttpResponse('removed')
            else:
                return HttpResponse('Unauthorized user.')
        except BaseException:
            return HttpResponse('Notification not found.')

    else:
        return render(request, 'website/templates/404.html')


@csrf_exempt
def ajax_keyword_search(request):
    if request.method == "POST":
        key = request.POST['key']
        questions = (
            Question.objects.filter(
                title__contains=key).filter(
                is_spam=False,
                is_active=True) | Question.objects.filter(
                category__name=key).filter(
                is_spam=False,
                is_active=True)).distinct().order_by('-date_created')
        context = {
            'questions': questions
        }
        return render(
            request,
            'website/templates/ajax-keyword-search.html',
            context)
    else:
        return render(request, 'website/templates/404.html')


def get_user_email(uid):
    user = User.objects.get(id=uid)
    user_email = user.email
    return user_email


def send_remider_mail():
    if date.today().weekday() == 1 or date.today().weekday() == 3 :
        #check in the database for last mail sent date
        try:
            is_mail_sent = Scheduled_Auto_Mail.objects\
                    .get(pk=1, is_sent=1, is_active=1)
            sent_date = is_mail_sent.mail_sent_date
        except Scheduled_Auto_Mail.DoesNotExist:
            sent_date = None
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        if sent_date == date_string:
            print("***** Mail already sent on ",sent_date, " *****")
            pass
        else:
            a = Cron()
            a.unanswered_notification()
            Scheduled_Auto_Mail.objects.get_or_create(id=1,defaults=dict(mail_sent_date=date_string,is_sent=1, is_active=1))
            Scheduled_Auto_Mail.objects.filter(is_sent=1).update(mail_sent_date=date_string)
            print("***** New Notification Mail sent *****")
            a.train_spam_filter()
    else:
        print("***** Mail not sent *****")
