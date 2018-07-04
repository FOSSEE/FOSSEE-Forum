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

User = get_user_model()
admins = (
   9, 4376, 4915, 14595, 12329, 22467, 5518, 30705
)
categories = FossCategory.objects.order_by('name')

# Function to check if user is in any moderator group
def is_moderator(user):
    return user.groups.count() > 0

# Function to check if user is anonymous, and if not he/she has first_name and last_name
def account_credentials_defined(user):
    return ((user.first_name and user.last_name) or is_moderator(user))

# for home page
def home(request):

    settings.MODERATOR_ACTIVATED = False

    questions = Question.objects.all().order_by('-date_created').filter(is_spam = False)
    context = {
        'categories': categories,
        'questions': questions,
    }

    return render(request, "website/templates/index.html", context)

# to get all questions posted till now and pagination, 20 questions at a time
def questions(request):
    questions = Question.objects.all().filter(is_spam = False).order_by('-date_created')
    context = {
        'questions': questions,
    }
    return render(request, 'website/templates/questions.html', context)

# get particular question, with votes,anwsers
def get_question(request, question_id = None, pretty_url = None):

    question = get_object_or_404(Question, id = question_id)
    sub_category = True

    if question.sub_category == "" or str(question.sub_category) == 'None':
        sub_category = False

    if (settings.MODERATOR_ACTIVATED):
        answers = question.answer_set.all()
    else:
        answers = question.answer_set.filter(is_spam = False).all()
    ans_count = len(answers)
    form = AnswerQuestionForm()
    thisuserupvote = question.userUpVotes.filter(id = request.user.id).count()
    thisuserdownvote = question.userDownVotes.filter(id = request.user.id).count()

    ans_votes = []
    for vote in answers:
        net_ans_count  = vote.num_votes
        ans_votes.append([vote.userUpVotes.filter(id = request.user.id).count(), vote.userDownVotes.filter(id = request.user.id).count(), net_ans_count])

    main_list = list(zip(answers, ans_votes))
    context = {
        'ans_count': ans_count,
        'question': question,
        'sub_category':sub_category,
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
    elif (question.userViews.filter(id = request.user.id).count() == 0):
        question.views += 1
        question.userViews.add(request.user)

    question.save()

    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    return render(request, 'website/templates/get-question.html', context)

# post answer to a question, send notification to the user, whose question is answered
# if anwser is posted by the owner of the question, no notification is sent
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def question_answer(request, question_id):

    context = {}
    question = get_object_or_404(Question, id = question_id)

    if (request.method == 'POST'):

        form = AnswerQuestionForm(request.POST, request.FILES)
        answer = Answer()
        answer.uid = request.user.id

        if form.is_valid():
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

            # if user_id of question does not match to user_id of answer, send notification
            if ((question.user.id != request.user.id) and (answer.is_spam == False)):
                notification = Notification()
                notification.uid = question.user.id
                notification.qid = question.id
                notification.aid = answer.id
                notification.save()

            #Sending email when a new answer is posted
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - Your question has been answered".format(question.category)
            to = [question.user.email, settings.FORUM_NOTIFICATION, ]
            message = """The following new answer has been posted in the FOSSEE Forum: \n\n
                Title: {0} \n
                Category: {1}\n
                Link: {2}\n\n

                Regards, \nFOSSEE Team, \nIIT Bombay.
                """.format(
                question.title,
                question.category,
                settings.DOMAIN_NAME + '/question/' + str(question_id) + "#answer" + str(answer.id)
            )
            send_mail(subject, message, sender_email, to, fail_silently = True)

            return HttpResponseRedirect('/question/{0}/'.format(question_id))

        else:
            context['form'] = form
            context['question'] = question

    else:
        form = AnswerQuestionForm()
        context['question'] = question

    context['form'] = form
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    context.update(csrf(request))
    return render(request, 'website/templates/get-question.html', context)


# comments for specific answer and notification is sent to owner of the answer
# notify other users in the comment thread
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def answer_comment(request):

    context = {}

    if (request.method == 'POST'):

        answer_id = request.POST['answer_id']
        answer = Answer.objects.get(pk = answer_id)
        answers = answer.question.answer_set.filter(is_spam = False).all()
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
            subject = "FOSSEE Forums - {0} - Comment for your answer".format(answer.question.category)
            to = [answer_creator.email, settings.FORUM_NOTIFICATION, ]
            message = """
                A comment has been posted on your answer. \n\n
                Title: {0}\n
                Category: {1}\n
                Link: {2}\n\n
                Regards, \nFOSSEE Team, \nIIT Bombay.
                """.format(
                answer.question.title,
                answer.question.category,
                settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
            )
            send_mail(subject, message, sender_email, to)

            # notifying other users in the comment thread
            uids = answer.answercomment_set.filter(answer = answer).values_list('uid', flat = True)
            answer_comments = answer.answercomment_set.filter(answer = answer)

            comment_creator_emails = []
            for c in answer_comments:
                comment_creator = c.user()
                email = comment_creator.email
                comment_creator_emails.append(email)
            comment_creator_emails.append(settings.FORUM_NOTIFICATION)

            # getting distinct uids
            uids = set(uids)
            uids.remove(request.user.id)
            for uid in uids:
                notification = Notification()
                notification.uid = uid
                notification.qid = answer.question.id
                notification.aid = answer.id
                notification.cid = comment.id
                notification.save()

            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - Comment has a reply".format(answer.question.category)
            to = comment_creator_emails
            message = """
                A reply has been posted on your comment.\n\n
                Title: {0}\n
                Category: {1}\n
                Link: {2}\n\n
                Regards, \nFOSSEE Team, \nIIT Bombay.
                """.format(
                answer.question.title,
                answer.question.category,
                settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
            )
            send_mail(subject, message, sender_email, to)

            return HttpResponseRedirect('/question/{0}/'.format(answer.question.id))

        else:
            context.update({
                'form': form,
                'question': answer.question,
                'answers': answers,
            })
            return render(request, 'website/templates/get-question.html', context)

    else:
        return render(request, 'website/templates/404.html')

# View used to filter question according to category
def filter(request, category = None, tutorial = None):

    if category and tutorial:
        questions = Question.objects.filter(category__name = category).filter(sub_category = tutorial).order_by('-date_created')
    elif tutorial is None:
        questions = Question.objects.filter(category__name = category).order_by('-date_created')

    if (not settings.MODERATOR_ACTIVATED):
        questions = questions.filter(is_spam = False)

    context = {
        'questions': questions,
        'category': category,
        'tutorial': tutorial,
    }

    return render(request, 'website/templates/filter.html',  context)

# post a new question on to forums, notification is sent to mailing list team@fossee.in
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def new_question(request):

    settings.MODERATOR_ACTIVATED = False

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
                    context['form'] = NewQuestionForm(category = category)
                    return render(request, 'website/templates/new-question.html', context)

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

            #Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            to = (question.category.email, settings.FORUM_NOTIFICATION)
            message = """
                The following new question has been posted in the FOSSEE Forum: <br>
                <b> Title: </b>{0}<br>
                <b> Category: </b>{1}<br>
                <b> Link: </b><a href="{3}">{3}</a><br>
                <b> Question : </b>{2}<br>
                <b> Classified as spam: </b>{4}<br>
                """.format(
                question.title,
                question.category,
                question.body,
                settings.DOMAIN_NAME + '/question/'+ str(question.id),
                question.is_spam,
            )
            email = EmailMultiAlternatives(
                subject, '',
                sender_email, to,
                headers = {"Content-type":"text/html;charset=iso-8859-1"}
            )
            email.attach_alternative(message, "text/html")
            email.send(fail_silently = True)

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
            return render(request, 'website/templates/new-question.html', context)

    else:
        category = request.GET.get('category')
        form = NewQuestionForm(category = category)
        context['category'] = category

    context['form'] = form
    context.update(csrf(request))
    return render(request, 'website/templates/new-question.html', context)

# Edit a question on forums, notification is sent to mailing list team@fossee.in
@login_required
@user_passes_test(account_credentials_defined, login_url='/accounts/profile/')
def edit_question(request, question_id):

    context = {}
    user = request.user
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    all_category = FossCategory.objects.all()
    question = get_object_or_404(Question, id = question_id)

    # To prevent random user from manually entering the link and editing
    if ((request.user.id != question.user.id or question.answer_set.count() > 0) and (not is_moderator(request.user))):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == 'POST'):

        previous_title = question.title
        form = NewQuestionForm(request.POST, request.FILES)
        question.title = '' # To prevent same title error in form
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

            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.is_spam = cleaned_data['is_spam']
            question.views = 1
            question.save()
            question.userViews.add(request.user)
            if str(question.sub_category) == 'None':
                question.sub_category = ""
            if (not settings.MODERATOR_ACTIVATED):
                if (predict(question.body) == "Spam"):
                    question.is_spam = True

            question.save()

            # Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            to = (question.user.email, question.category.email, settings.FORUM_NOTIFICATION)
            message = """
                The following question has been edited in the FOSSEE Forum: <br>
                <b> Original title: </b>{0}<br>
                <b> New title: </b?{1}<br>
                <b> Category: </b>{2}<br>
                <b> Link: </b><a href="{4}">{4}</a><br>
                <b> Question : </b>{3}<br>
                <b> Classified as spam: </b>{5}<br>
                """.format(
                question.title,
                previous_title,
                question.category,
                question.body,
                settings.DOMAIN_NAME + '/question/'+ str(question.id),
                question.is_spam,
            )
            email = EmailMultiAlternatives(
                subject, '',
                sender_email, to,
                headers = {"Content-type":"text/html;charset=iso-8859-1"}
            )
            email.attach_alternative(message, "text/html")
            email.send(fail_silently = True)

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
            return render(request, 'website/templates/edit-question.html', context)

    else:
        form = NewQuestionForm(instance = question)

    context['form'] = form
    context.update(csrf(request))
    return render(request, 'website/templates/edit-question.html', context)

# View for deleting question, notification is sent to mailing list team@fossee.in
@login_required
def question_delete(request, question_id):

    question = get_object_or_404(Question, id = question_id)
    title = question.title

    # To prevent random user from manually entering the link and deleting
    if ((request.user.id != question.user.id or question.answer_set.count() > 0) and (not settings.MODERATOR_ACTIVATED)):
        return render(request, 'website/templates/not-authorized.html')

    if (request.method == "POST"):

        # Send a delete email only when moderator does so
        if (settings.MODERATOR_ACTIVATED):

            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            to = (question.user.email, settings.FORUM_NOTIFICATION)
            delete_reason = request.POST['deleteQuestion']
            message = """
                The following question has been deleted by a moderator of the FOSSEE Forum: <br>
                <b> Title: </b>{0}<br>
                <b> Category: </b>{1}<br>
                <b> Question: </b>{2}<br>
                <b> Moderator comments: </b>{3}<br>
                """.format(
                title,
                question.category,
                question.body,
                delete_reason,
            )
            send_mail(subject, message, sender_email, to, fail_silenty = True)

    question.delete()
    return render(request, 'website/templates/question-delete.html', {'title': title})

# View for deleting answer, notification is sent to person who posted answer
@login_required
@user_passes_test(is_moderator)
def answer_delete(request, answer_id):

    answer = get_object_or_404(Answer, id = answer_id)
    question_id = answer.question.id

    if (request.method == "POST"):

        # Sending email to user when answer is deleted
        sender_name = "FOSSEE Forums"
        sender_email = settings.SENDER_EMAIL
        subject = "FOSSEE Forums - {0} - Answer Deleted".format(answer.question.category)
        to = [answer.user().email]
        delete_reason = request.POST['deleteAnswer']
        message = """
            The following answer has been deleted by a moderator in the FOSSEE Forum: <br>
            <b> Answer: </b>{0}<br>
            <b> Category: </b>{1}<br>
            <b> Question: </b>{2}<br>
            <b> Moderator comments: </b>{3}<br>
            """.format(
            answer.body,
            answer.question.category,
            answer.question.body,
            delete_reason,
        )
        send_mail(subject, message, sender_email, to, fail_silently = True)

    answer.delete()
    return HttpResponseRedirect('/question/{0}/'.format(question_id))

# View to mark answer as spam/non-spam
@login_required
@user_passes_test(is_moderator)
def mark_answer_spam(request, answer_id):

    answer = get_object_or_404(Answer, id = answer_id)
    question_id = answer.question.id

    if (request.method == "POST"):
        type = request.POST['selector']
        if (type == "spam"):
            answer.is_spam = True
        else:
            answer.is_spam = False

    answer.save()
    return HttpResponseRedirect('/question/{0}/#answer{1}/'.format(question_id, answer.id))

# return number of votes and initial votes
# user who asked the question,cannot vote his/or anwser,
# other users can post votes
@login_required
def vote_post(request):

    post_id = int(request.POST.get('id'))
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    cur_post = get_object_or_404(Question, id = post_id)
    thisuserupvote = cur_post.userUpVotes.filter(id = request.user.id).count()
    thisuserdownvote = cur_post.userDownVotes.filter(id = request.user.id).count()
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
    cur_post = get_object_or_404(Answer, id = post_id)
    thisuserupvote = cur_post.userUpVotes.filter(id = request.user.id).count()
    thisuserdownvote = cur_post.userDownVotes.filter(id = request.user.id).count()
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

    settings.MODERATOR_ACTIVATED = False

    if (user_id == request.user.id):
        try:
            notifications = Notification.objects.filter(uid = user_id).order_by('-date_created')
            context = {
                'notifications': notifications,
            }
            return render(request, 'website/templates/notifications.html', context)
        except:
            return HttpResponseRedirect("/user/{0}/notifications/".format(request.user.id))

    else:
        return render(request, 'website/templates/not-authorized.html')


# to clear notification from header, once viewed or cancelled
@login_required
def clear_notifications(request):
    settings.MODERATOR_ACTIVATED = False
    Notification.objects.filter(uid = request.user.id).delete()
    return HttpResponseRedirect("/user/{0}/notifications/".format(request.user.id))

def search(request):
    settings.MODERATOR_ACTIVATED = False
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

    # If user is a master moderator
    if (request.user.groups.filter(name = "forum_moderator").exists()):
        questions = Question.objects.all().order_by('-date_created')
        categories = FossCategory.objects.order_by('name')

    else:
        # Finding the moderator's categories
        categories = []
        for group in request.user.groups.all():
            categories.append(ModeratorGroup.objects.get(group = group).category)
        # Getting the questions related to moderator's categories
        questions = []
        for category in categories:
            questions.extend(Question.objects.filter(category__name = category.name).order_by('-date_created'))

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
    if (request.user.groups.filter(name = "forum_moderator").exists()):
        questions = Question.objects.all().order_by('-date_created')
        if ('spam' in request.GET):
            questions = questions.filter(is_spam = True)
        elif ('non-spam' in request.GET):
            questions = questions.filter(is_spam = False)

    else:
        # Finding the moderator's category questions
        questions = []
        for group in request.user.groups.all():
            category = ModeratorGroup.objects.get(group = group).category
            questions_to_add = Question.objects.filter(category__name = category.name).order_by('-date_created')
            if ('spam' in request.GET):
                questions_to_add = questions_to_add.filter(is_spam = True)
            elif ('non-spam' in request.GET):
                questions_to_add = questions_to_add.filter(is_spam = False)
            questions.extend(questions_to_add)

    context = {
        'questions': questions,
    }

    return render(request, 'website/templates/moderator/questions.html', context)

# Unanswered questions page for moderator
@login_required
@user_passes_test(is_moderator)
def moderator_unanswered(request):

    # If user is a master moderator
    if (request.user.groups.filter(name = "forum_moderator").exists()):
        questions = Question.objects.all().filter(is_spam = True).order_by('date_created').reverse()

    else:
        # Finding the moderator's category questions
        questions = []
        for group in request.user.groups.all():
            category = ModeratorGroup.objects.get(group = group).category
            questions.extend(Question.objects.filter(category__name = category.name).order_by('-date_created'))

    context = {
        'questions': questions,
    }

    return render(request, 'website/templates/moderator/unanswered.html', context)

# Re-training spam filter
@login_required
@user_passes_test(is_moderator)
def train_spam_filter(request):

    train()
    return HttpResponseRedirect('/moderator/')

# AJAX SECTION
# All the ajax views go below
@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':

        category = request.POST.get('category')

        if (SubFossCategory.objects.filter(parent_id = category).exists()):
            tutorials = SubFossCategory.objects.filter(parent_id = category)
            context = {
                'tutorials': tutorials,
            }
            return render(request, 'website/templates/ajax-tutorials.html', context)

        else:
            return HttpResponse('No sub-category in category.')
    
    else:
        return render(request, 'website/templates/404.html')

@csrf_exempt
def ajax_answer_update(request):
    if request.method == 'POST':
        aid = request.POST['answer_id']
        body = request.POST['answer_body']

        try:
            answer = get_object_or_404(Answer, pk = aid)
            if (is_moderator(request.user)):
                answer.body = str(body)
                answer.save()
                return HttpResponse('saved')
            else:
                return HttpResponse('Only moderator can update.')
        except:
            return HttpResponse('Answer not found.')

    else:
        return render(request, 'website/templates/404.html')

@csrf_exempt
def ajax_answer_comment_delete(request):
    if request.method == 'POST':
        comment_id = request.POST['comment_id']

        try:
            comment = get_object_or_404(AnswerComment, pk = comment_id)
            if (is_moderator(request.user)):
                comment.delete()
                return HttpResponse('deleted')
            else:
                return HttpResponse('Only moderator can delete.')
        except:
            return HttpResponse('Comment not found.')

    else:
        return render(request, 'website/templates/404.html')

@csrf_exempt
def ajax_notification_remove(request):
    if request.method == "POST":

        nid = request.POST["notification_id"]
        
        try:
            notification = get_object_or_404(Notification, pk = nid)
            if (notification.uid == request.user.id):
                notification.delete()
                return HttpResponse('removed')
            else:
                return HttpResponse('Unauthorized user.')
        except:
            return HttpResponse('Notification not found.')
    
    else:
        return render(request, 'website/templates/404.html')

@csrf_exempt
def ajax_keyword_search(request):
    if request.method == "POST":
        key = request.POST['key']

        questions = Question.objects.filter(title__contains = key).filter(is_spam=False)
        context = {
            'questions': questions
        }

        return render(request, 'website/templates/ajax-keyword-search.html', context)
    
    else:
        return render(request, 'website/templates/404.html')