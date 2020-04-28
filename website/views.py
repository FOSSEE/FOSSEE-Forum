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
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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


# NON-VIEWS FUNCTIONS

def send_email(subject, plain_message, html_message, from_email, to, bcc=None, cc=None, reply_to=None):
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        from_email,
        to,
        bcc=bcc,
        cc=cc,
        reply_to=reply_to,
        headers={"Content-type": "text/html;charset=iso-8859-1"},
    )
    email.attach_alternative(html_message, "text/html")
    # email.content_subtype = 'html'  # Main content is text/html (No need to use EmailMultiAlternatives for this)
    # email.mixed_subtype = 'related'  # if you are sending attachment with content id, subtype must be 'related'.
    email.send(fail_silently=True)

def send_email_as_to(subject, plain_message, html_message, from_email, to, reply_to=None):
    connection = mail.get_connection(fail_silently=True)

    messages = []
    for to_email in to:
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            from_email,
            [to_email],
            reply_to=reply_to,
            headers={"Content-type": "text/html;charset=iso-8859-1"},
        )
        email.attach_alternative(html_message, "text/html")
        messages.append(email)

    connection.send_messages(messages)




# Function to check if user is in any moderator group or to check whether user belongs to the moderator group of question's category


def is_moderator(user, question=None):
    if question:
        # REQUIRES CHANGES
        # If we add a new Category and don't create a Moderator Group for it, it will throw Exception.
        # Maybe just handle the Exception
        return user.groups.filter(moderatorgroup=ModeratorGroup.objects.get(category=question.category)).exists()
    return user.groups.count() > 0

# Function to check if user is anonymous, and if not he/she has first_name
# and last_name


def account_credentials_defined(user):
    return ((user.first_name and user.last_name) or is_moderator(user))

# for home page


def home(request):
    send_remider_mail()
    
    # CHANGES REQUIRED
    # Should be redirected to /moderator/ if Moderator Panel is activated instead of deavtivating it
    # Creating seperate views for activating/deactivating is an option
    if request.session.get('MODERATOR_ACTIVATED', False):
        request.session['MODERATOR_ACTIVATED'] = False

    next = request.GET.get('next', '')
    next = next.split('/')
    if 'moderator' in next:
        next.remove('moderator')
    next = '/'.join(next)
    try:
        resolve(next)   # Checks if there is a view corresponding to this URL, throws a Resolver404 Exception otherwise
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
    if request.session.get('MODERATOR_ACTIVATED', False):
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
    if request.session.get('MODERATOR_ACTIVATED', False):
        if is_moderator(request.user, get_object_or_404(Question, id=question_id)):
            question = get_object_or_404(Question, id=question_id)
            answers = question.answer_set.all()
        else:
            return HttpResponseRedirect("/moderator/")
    else:
        # SHOULD SPAMMED QUESTIONS BE VISIBLE TO THE AUTHOR??
        question = get_object_or_404(Question, id=question_id, is_active=True, is_spam=False)
        answers = question.answer_set.filter(is_active=True).all()

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


# Returns the mail ids of all people linked to the question.
# That is, who posted the question and all who posted the answers and comments.

def to_uids(question):
    mail_uids = [question.user.id]
    answers = Answer.objects.filter(question_id=question.id, is_active=True).distinct()
    for answer in answers:
        for comment in AnswerComment.objects.values('uid').filter(answer=answer, is_active=True).distinct():
            mail_uids.append(comment['uid'])
        mail_uids.append(answer.uid)
    mail_uids = set(mail_uids)
    return mail_uids


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

            # SENDING EMAILS AND NOTIFICATIONS ABOUT NEW ANSWER
            from_email = settings.SENDER_EMAIL
            html_message = render_to_string('website/templates/emails/new_answer_email.html', {
                'title': question.title,
                'category': question.category,
                'link': settings.DOMAIN_NAME + '/question/' + str(question.id) + "#answer" + str(answer.id),
            })
            plain_message = strip_tags(html_message)

            # Notifying the Question Author
            if question.user.id != request.user.id and answer.is_spam == False:
                notification = Notification(uid=question.user.id, qid=question.id, aid=answer.id)
                notification.save()

                subject = "FOSSEE Forums - {0} - Your question has been answered".format(question.category)
                to = [question.user.email]
                send_email(subject, plain_message, html_message, from_email, to)

            # Email and Notification for all user in this thread
            mail_uids = to_uids(question)
            mail_uids.difference_update({question.user.id, request.user.id})

            subject = "FOSSEE Forums - {0} - Question has been answered".format(question.category)
            to = [settings.BCC_EMAIL_ID]
            
            for mail_uid in mail_uids:
                notification = Notification(uid=mail_uid, qid=question.id, aid=answer.id)
                notification.save()

                # Appending user email in 'to' list
                to.append(get_user_email(mail_uid))

            # Sending Email to everyone in 'to' list individually
            send_email_as_to(subject, plain_message, html_message, from_email, to)
            
            return HttpResponseRedirect('/question/{0}/'.format(question_id))

        else:
            messages.error(request, "Answer can't be empty or only blank spaces.")

    return HttpResponseRedirect('/question/{0}/'.format(question_id))


# comments for specific answer and notification is sent to owner of the answer
# notify other users in the comment thread
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def answer_comment(request):

    if (request.method == 'POST'):

        answer_id = request.POST['answer_id']
        answer = Answer.objects.get(pk=answer_id, is_active=True)
        # answers = answer.question.answer_set.filter(is_spam=False, is_active=True).all()
        answer_creator = answer.user()
        form = AnswerCommentForm(request.POST)

        if form.is_valid():

            body = request.POST['body']
            comment = AnswerComment(uid=request.user.id, answer=answer, body=body)
            comment.save()

            # SENDING EMAILS AND NOTIFICATIONS ABOUT NEW COMMENT
            from_email = settings.SENDER_EMAIL
            html_message = render_to_string('website/templates/emails/new_comment_email.html', {
                'title': answer.question.title,
                'category': answer.question.category,
                'link': settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#comment" + str(comment.id),
            })
            plain_message = strip_tags(html_message)

            not_to_notify = [request.user.id]

            # Notifying the Question Author
            if answer.question.user.id not in not_to_notify:
                notification = Notification(uid=answer.question.user.id, qid=answer.question.id, aid=answer.id, cid=comment.id)
                notification.save()

                subject = "FOSSEE Forums - {0} - New Comment under your Question".format(answer.question.category)
                to = [answer.question.user.email]
                send_email(subject, plain_message, html_message, from_email, to)

                not_to_notify.append(answer.question.user.id)

            # Notifying the Answer Author
            if answer.uid not in not_to_notify:
                notification = Notification(uid=answer.uid, qid=answer.question.id, aid=answer.id, cid=comment.id)
                notification.save()

                subject = "FOSSEE Forums - {0} - New Comment on your answer".format(answer.question.category)
                to = [answer_creator.email]
                send_email(subject, plain_message, html_message, from_email, to)

                not_to_notify.append(answer.uid)

            # Notifying the Last Comment Author
            answer_comments = AnswerComment.objects.filter(answer=answer, is_active=True).exclude(uid=request.user.id).order_by('-date_created')
            if answer_comments.exists() and answer_comments[0].uid not in not_to_notify:
                last_comment = answer_comments[0]

                notification = Notification(uid=last_comment.uid, qid=answer.question.id, aid=answer.id, cid=comment.id)
                notification.save()

                subject = "FOSSEE Forums - {0} - Your Comment has a Reply".format(answer.question.category)
                to = [get_user_email(last_comment.uid)]
                send_email(subject, plain_message, html_message, from_email, to)

                not_to_notify.append(last_comment.uid)

            # Notifying all other users in the thread
            mail_uids = to_uids(answer.question)
            mail_uids.difference_update(set(not_to_notify))
            
            subject = "FOSSEE Forums - {0} - New Comment under the Question".format(answer.question.category)

            to = [settings.BCC_EMAIL_ID]
            for mail_uid in mail_uids:
                notification = Notification(uid=mail_uid, qid=answer.question.id, aid=answer.id, cid=comment.id)
                notification.save()

                # Appending user email in 'to' list                
                to.append(get_user_email(mail_uid))

            # Sending Email to everyone in 'to' list individually
            send_email_as_to(subject, plain_message, html_message, from_email, to)

            return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))

        else:
            messages.error(request, "Comment cann't be empty or only blank spaces.")
            return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))
    
    return render(request, '404.html')

# View used to filter question according to category


def filter(request, category=None, tutorial=None):

    if category and tutorial:
        questions = Question.objects.filter(
            category__name=category).filter(
            sub_category=tutorial).order_by('-date_created')
    elif tutorial is None:
        questions = Question.objects.filter(
            category__name=category).order_by('-date_created')

    if (not request.session.get('MODERATOR_ACTIVATED', False)):
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

    if request.session.get('MODERATOR_ACTIVATED', False):
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
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            from_email = settings.SENDER_EMAIL
            to = [question.category.email]
            html_message = render_to_string('website/templates/emails/new_question_email.html', {
                'title': question.title,
                'category': question.category,
                'body': question.body,
                'link': settings.DOMAIN_NAME + '/question/' + str(question.id),
            })
            plain_message = strip_tags(html_message)
            send_email(subject, plain_message, html_message, from_email, to)

            # Second Email with spam classification
            to = [settings.BCC_EMAIL_ID]
            html_message = render_to_string('website/templates/emails/new_question_email.html', {
                'title': question.title,
                'category': question.category,
                'body': question.body,
                'link': settings.DOMAIN_NAME + '/question/' + str(question.id),
                'spam': question.is_spam,
            })
            plain_message = strip_tags(html_message)
            send_email(subject, plain_message, html_message, from_email, to)

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
    if ((request.user.id != question.user.id or question.answer_set.filter(is_active=True).count() > 0) and 
            (not is_moderator(request.user, question) or not request.session.get('MODERATOR_ACTIVATED', False))):
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
                    return render(request, 'website/templates/edit-question.html', context)

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
            if (not request.session.get('MODERATOR_ACTIVATED', False)):
                if (predict(question.body) == "Spam"):
                    question.is_spam = True

            question.save()

            # Sending Email Notifications about Question Edit
            subject = "FOSSEE Forums - {0} - Question Edited".format(question.category)
            from_email = settings.SENDER_EMAIL
            html_message = render_to_string('website/templates/emails/edited_question_email.html', {
                'title': question.title,
                'previous_title': previous_title,
                'category': question.category,
                'body': question.body,
                'link': settings.DOMAIN_NAME + '/question/' + str(question.id),
            })
            plain_message = strip_tags(html_message)
            to = [question.category.email, settings.FORUM_NOTIFICATION]

            # Getting emails of everyone in Question Thread and appending in 'to'
            # IF MODERATOR_ACTIVATED
            mail_uids = to_uids(question)
            for uid in mail_uids:
                to.append(get_user_email(uid))

            send_email_as_to(subject, plain_message, html_message, from_email, to)

            if (question.is_spam and not request.session.get('MODERATOR_ACTIVATED', False)):
                return HttpResponseRedirect('/')

            return HttpResponseRedirect('/question/{0}/'.format(question.id))

        else:

            context.update(csrf(request))
            category = request.POST.get('category', None)
            tutorial = request.POST.get('tutorial', None)
            context['category'] = category
            context['tutorial'] = tutorial
            context['form'] = form
            return render(request, 'website/templates/edit-question.html', context)

    else:
        form = NewQuestionForm(instance=question)

    context['form'] = form
    context.update(csrf(request))
    return render(request, 'website/templates/edit-question.html', context)


def add_Spam(question_body, is_spam):
    xfile = openpyxl.load_workbook(
        settings.BASE_DIR + '/Spam_Filter_Data/DataSet.xlsx')
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

    # To prevent random user from manually entering the link and deleting
    # NOT NEEDED THOUGH AS ONLY ALLOWED USERS CAN SEND POST REQUEST FROM TEMPLATE
    if ((request.user.id != question.user.id or question.answer_set.filter(is_active=True).count() > 0) and 
            (not is_moderator(request.user, question) or not request.session.get('MODERATOR_ACTIVATED', False))):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == "POST"):
        question.is_active = False
        question.save()

        # Send a delete email only when moderator does so
        if request.session.get('MODERATOR_ACTIVATED', False):
            delete_reason = request.POST.get('deleteQuestion')

            subject = "FOSSEE Forums - {0} - Question Deleted".format(question.category)
            from_email = settings.SENDER_EMAIL
            to = [settings.BCC_EMAIL_ID]
            html_message = render_to_string('website/templates/emails/deleted_question_email.html', {
                'title': question.title,
                'category': question.category,
                'body': question.body,
                'reason': delete_reason,
            })
            plain_message = strip_tags(html_message)
            
            mail_uids = to_uids(question)
            for uid in mail_uids:
                to.append(get_user_email(uid))

            send_email_as_to(subject, plain_message, html_message, from_email, to)

        return render(request, 'website/templates/question-delete.html', {'title': question.title})
    
    # Question can only be deleted by sending POST requests and not by GET requests (directly accessing the link)
    return render(request, 'website/templates/not-authorized.html')


@login_required
@user_passes_test(is_moderator)
def question_restore(request, question_id):
    question = get_object_or_404(Question, id=question_id, is_active=False)

    if not is_moderator(request.user, question) or not request.session.get('MODERATOR_ACTIVATED', False):
        return render(request, 'website/templates/not-authorized.html')

    question.is_active = True
    question.save()

    return HttpResponseRedirect('/question/{0}/'.format(question_id))

# View for deleting answer, notification is sent to person who posted answer
# @user_passes_test(is_moderator)
@login_required
def answer_delete(request, answer_id):

    answer = get_object_or_404(Answer, id=answer_id, is_active=True)
    question_id = answer.question.id

    # The second statement in if condition excludes comments made by Answer's author.
    # NOT NEEDED THOUGH AS ONLY ALLOWED USERS CAN SEND POST REQUEST FROM TEMPLATE
    if ((request.user.id != answer.uid or AnswerComment.objects.filter(answer=answer, is_active=True).exclude(uid=answer.uid).exists()) and
            (not is_moderator(request.user, answer.question) or not request.session.get('MODERATOR_ACTIVATED', False))):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == "POST"):
        answer.is_active = False
        answer.save()

        # Sending Emails for Answer Delete
        subject = "FOSSEE Forums - {0} - Answer Deleted".format(answer.question.category)
        from_email = settings.SENDER_EMAIL
        to = [settings.BCC_EMAIL_ID, answer.question.user.email]
        
        if request.session.get('MODERATOR_ACTIVATED', False):
            delete_reason = request.POST.get('deleteAnswer')

            html_message = render_to_string('website/templates/emails/deleted_answer_email.html', {
                'title': answer.question.title,
                'category': answer.question.category,
                'body': answer.question.body,
                'answer': answer.body,
                'reason': delete_reason,
                'by_moderator': True,
            })
            plain_message = strip_tags(html_message)

            to.append(get_user_email(answer.uid))
            for comment in AnswerComment.objects.filter(answer=answer, is_active=True):
                to.append(get_user_email(comment.uid))

            to = list(set(to))   # Removing Duplicates
            send_email_as_to(subject, plain_message, html_message, from_email, to)
        else:
            html_message = render_to_string('website/templates/emails/deleted_answer_email.html', {
                'title': answer.question.title,
                'category': answer.question.category,
                'body': answer.question.body,
                'answer': answer.body,
            })
            plain_message = strip_tags(html_message)

            to.append(answer.question.category.email)
            send_email_as_to(subject, plain_message, html_message, from_email, to)

        return HttpResponseRedirect('/question/{0}/'.format(question_id))

    # Answer can only be deleted by sending POST requests and not by GET requests (directly accessing the link)
    return render(request, 'website/templates/not-authorized.html')


@login_required
@user_passes_test(is_moderator)
def answer_restore(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id, is_active=False)

    if not is_moderator(request.user, answer.question) or not request.session.get('MODERATOR_ACTIVATED', False):
        return render(request, 'website/templates/not-authorized.html')

    if not answer.question.is_active:
        messages.error(request, "Answer can only be restored when its question is not deleted.")
        return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))

    answer.is_active = True
    answer.save()

    return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))


# COMMENT DELETION IS THROUGH AJAX

@login_required
@user_passes_test(is_moderator)
def comment_restore(request, comment_id):
    comment = get_object_or_404(AnswerComment, id=comment_id, is_active=False)

    if not is_moderator(request.user, comment.answer.question) or not request.session.get('MODERATOR_ACTIVATED', False):
        return render(request, 'website/templates/not-authorized.html')

    if not comment.answer.is_active:
        messages.error(request, "Comment can only be restored when its answer is not deleted")
        return HttpResponseRedirect('/question/{0}/'.format(comment.answer.question.id))

    comment.is_active = True
    comment.save()

    return HttpResponseRedirect('/question/{0}/'.format(comment.answer.question.id))

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

    if request.session.get('MODERATOR_ACTIVATED', False):
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
    request.session['MODERATOR_ACTIVATED'] = False   # WHY ??? Instead Moderator shouldn't be allowed to access it.
    Notification.objects.filter(uid=request.user.id).delete()
    return HttpResponseRedirect(
        "/user/{0}/notifications/".format(request.user.id))


def search(request):
    if request.session.get('MODERATOR_ACTIVATED', False):
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

    request.session['MODERATOR_ACTIVATED'] = True
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

    # CHANGES REQUIRED
    # No checks here if Moderator Panel is activated or not

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

    request.session['MODERATOR_ACTIVATED'] = True   # Why here???
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

    # CHANGES REQUIRED
    # Should be accessable only if Moserator Panel is activated

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
        return render(request, '404.html')


@login_required
def ajax_answer_update(request):

    if request.method == 'POST':
        aid = request.POST['answer_id']
        body = request.POST['answer_body']
        answer = get_object_or_404(Answer, pk=aid, is_active=True)
        if ((request.user.id == answer.uid and not AnswerComment.objects.filter(answer=answer, is_active=True).exclude(uid=answer.uid).exists()) or
                (is_moderator(request.user, answer.question) and request.session.get('MODERATOR_ACTIVATED', False))):
            answer.body = str(body)
            answer.save()

            # Sending Emails regarding Answer Update
            subject = "FOSSEE Forums - {0} - Answer Edited".format(answer.question.category)
            from_email = settings.SENDER_EMAIL
            to = [settings.BCC_EMAIL_ID]

            if request.session.get('MODERATOR_ACTIVATED', False):

                html_message = render_to_string('website/templates/emails/edited_answer_email.html', {
                    'title': answer.question.title,
                    'category': answer.question.category,
                    'body': answer.question.body,
                    'link': settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id),
                    'by_moderator': True,
                })
                plain_message = strip_tags(html_message)

                mail_uids = to_uids(answer.question)
                for uid in mail_uids:
                    to.append(get_user_email(uid))

                send_email_as_to(subject, plain_message, html_message, from_email, to)

            else:
                html_message = render_to_string('website/templates/emails/edited_answer_email.html', {
                    'title': answer.question.title,
                    'category': answer.question.category,
                    'body': answer.question.body,
                    'link': settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id),
                })
                plain_message = strip_tags(html_message)

                to.append(answer.question.user.email)
                send_email_as_to(subject, plain_message, html_message, from_email, to)

            messages.success(request, "Answer is Successfully Saved!")
            return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))
        else:
            messages.error(request, "Failed to Update Answer!")
            return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))
    else:
        return render(request, '404.html')


@login_required
@csrf_exempt
def ajax_answer_comment_delete(request):
    if request.method == 'POST':
        comment_id = request.POST['comment_id']
        comment = get_object_or_404(AnswerComment, pk=comment_id)

        if ((is_moderator(request.user, comment.answer.question) and request.session.get('MODERATOR_ACTIVATED', False)) or
                (request.user.id == comment.uid and can_delete(comment.answer, comment_id))):
            comment.is_active = False
            comment.save()

            # Sending Emails regarding Comment Deletion
            subject = "FOSSEE Forums - {0} - Comment Deleted".format(comment.answer.question.category)
            from_email = settings.SENDER_EMAIL
            to = [settings.BCC_EMAIL_ID]

            if request.session.get('MODERATOR_ACTIVATED', False):
                html_message = render_to_string('website/templates/emails/deleted_comment_email.html', {
                    'title': comment.answer.question.title,
                    'category': comment.answer.question.category,
                    'body': comment.answer.question.body,
                    'answer': comment.answer.body,
                    'comment': comment.body,
                    'by_moderator': True,
                })
                plain_message = strip_tags(html_message)

                mail_uids = to_uids(comment.answer.question)
                for uid in mail_uids:
                    to.append(get_user_email(uid))

                send_email_as_to(subject, plain_message, html_message, from_email, to)

            else:
                html_message = render_to_string('website/templates/emails/deleted_comment_email.html', {
                    'title': comment.answer.question.title,
                    'category': comment.answer.question.category,
                    'body': comment.answer.question.body,
                    'answer': comment.answer.body,
                    'comment': comment.body,
                })
                plain_message = strip_tags(html_message)

                to.append(get_user_email(comment.answer.uid))
                send_email_as_to(subject, plain_message, html_message, from_email, to)


            return HttpResponse('deleted')
        else:
            messages.error(request, "Only Moderator can delete.")
            return HttpResponseRedirect(
                '/question/{0}/'.format(comment.answer.question.id))
    else:
        return render(request, '404.html')


@login_required
@csrf_exempt
def ajax_answer_comment_update(request):
    if request.method == 'POST':
        cid = request.POST['comment_id']
        body = request.POST['comment_body']
        comment = get_object_or_404(AnswerComment, pk=cid, is_active=True)

        if ((is_moderator(request.user, comment.answer.question) and request.session.get('MODERATOR_ACTIVATED', False)) or
                (request.user.id == comment.uid and can_delete(comment.answer, cid))):
            comment.body = str(body)
            comment.save()

            # Sending Emails regarding Comment Updation
            subject = "FOSSEE Forums - {0} - Comment Edited".format(comment.answer.question.category)
            from_email = settings.SENDER_EMAIL
            to = [settings.BCC_EMAIL_ID]

            if request.session.get('MODERATOR_ACTIVATED', False):
                html_message = render_to_string('website/templates/emails/edited_comment_email.html', {
                    'title': comment.answer.question.title,
                    'category': comment.answer.question.category,
                    'body': comment.answer.question.body,
                    'link': settings.DOMAIN_NAME + '/question/' + str(comment.answer.question.id) + "#comment" + str(comment.id),
                    'by_moderator': True,
                })
                plain_message = strip_tags(html_message)

                mail_uids = to_uids(comment.answer.question)
                mail_uids.discard(request.user.id)
                for uid in mail_uids:
                    to.append(get_user_email(uid))

                send_email_as_to(subject, plain_message, html_message, from_email, to)
            else:
                html_message = render_to_string('website/templates/emails/edited_comment_email.html', {
                    'title': comment.answer.question.title,
                    'category': comment.answer.question.category,
                    'body': comment.answer.question.body,
                    'link': settings.DOMAIN_NAME + '/question/' + str(comment.answer.question.id) + "#comment" + str(comment.id),
                })
                plain_message = strip_tags(html_message)

                to.append(get_user_email(comment.answer.uid))
                send_email_as_to(subject, plain_message, html_message, from_email, to)

            messages.success(request, "Comment is Successfully Saved")
            return HttpResponseRedirect('/question/{0}/'.format(comment.answer.question.id))
        else:
            messages.error(request, "Only moderator can update.")
            return HttpResponseRedirect('/question/{0}/'.format(comment.answer.question.id))
    else:
        return render(request, '404.html')


def can_delete(answer, comment_id):
    comments = answer.answercomment_set.filter(is_active=True).all()
    for c in comments:
        if c.id > int(comment_id):
            return False
    return True


@login_required
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
        return render(request, '404.html')


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
        return render(request, '404.html')


def get_user_email(uid):
    user = User.objects.get(id=uid)
    user_email = user.email
    return user_email


def send_remider_mail():
    if date.today().weekday() == 1 or date.today().weekday() == 3:
        # check in the database for last mail sent date
        try:
            is_mail_sent = Scheduled_Auto_Mail.objects\
                .get(pk=1, is_sent=1, is_active=1)
            sent_date = is_mail_sent.mail_sent_date
        except Scheduled_Auto_Mail.DoesNotExist:
            sent_date = None
        now = datetime.now()
        date_string = now.strftime("%Y-%m-%d")
        if sent_date == date_string:
            print("***** Mail already sent on ", sent_date, " *****")
            pass
        else:
            a = Cron()
            a.unanswered_notification()
            Scheduled_Auto_Mail.objects.get_or_create(id=1, defaults=dict(
                mail_sent_date=date_string, is_sent=1, is_active=1))
            Scheduled_Auto_Mail.objects.filter(
                is_sent=1).update(mail_sent_date=date_string)
            print("***** New Notification Mail sent *****")
            a.train_spam_filter()
    else:
        print("***** Mail not sent *****")
