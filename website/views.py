import re
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,render_to_response
from django.template.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages 
from django.utils.html import strip_tags
from website.models import Question, Answer, Notification, AnswerComment, FossCategory, Profile, SubFossCategory
from website.forms import NewQuestionForm, AnswerQuestionForm,AnswerCommentForm
from website.helpers import get_video_info, prettify
from django.db.models import Count
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from forums.settings import SET_TO_EMAIL_ID
from spamFilter import predict

User = get_user_model()
admins = (
   9, 4376, 4915, 14595, 12329, 22467, 5518, 30705
)
categories = FossCategory.objects.order_by('name')

# for home page
def home(request):
    print settings.DOMAIN_NAME
    questions = Question.objects.all().order_by('date_created').filter(is_spam=0).reverse()[:10]
    context = {
        'categories': categories,
        'questions': questions
    }
    return render(request, "website/templates/index.html", context)
    
# to get all questions posted till now and pagination, 20 questions at a time
def questions(request):
    questions = Question.objects.all().filter(is_spam=0).order_by('date_created').reverse()
    context = {
        'questions': questions,
    }
    return render(request, 'website/templates/questions.html', context)
    
# get particular question, with votes,anwsers
def get_question(request, question_id=None, pretty_url=None):

    question = get_object_or_404(Question, id=question_id)
    sub_category = True

    if question.sub_category == "" or str(question.sub_category) == 'None':
        sub_category = False
    else:
        sub_category = True

    pretty_title = prettify(question.title)
    if pretty_url != pretty_title:
        return HttpResponseRedirect('/question/'+ question_id + '/' + pretty_title)

    answers = question.answer_set.all()
    ans_count = question.answer_set.count()
    form = AnswerQuestionForm()
    thisuserupvote = question.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = question.userDownVotes.filter(id=request.user.id).count()
    net_count = question.userUpVotes.count() - question.userDownVotes.count()

    ans_votes = []
    for vote in answers:
        net_ans_count  = vote.userUpVotes.count() - vote.userDownVotes.count()
        ans_votes.append([vote.userUpVotes.filter(id=request.user.id).count(),vote.userDownVotes.filter(id=request.user.id).count(),net_ans_count])

    #for (f,b) in zip(foo, bar):
    main_list = zip(answers,ans_votes)
    context = {
        'ans_count': ans_count,
        'question': question,
        'sub_category':sub_category,
        'main_list': main_list,
        'form': form,
        'thisUserUpvote': thisuserupvote,
        'thisUserDownvote': thisuserdownvote,
        'net_count': net_count,
        'num_votes':question.num_votes,
        'ans_votes':ans_votes
    }
    context.update(csrf(request))

    # updating views count
    if (request.user.is_anonymous()):  # if no one logged in
        question.views += 1
    elif (question.userViews.filter(id=request.user.id).count() == 0):
        question.views += 1
        question.userViews.add(request.user)
    
    question.save()

    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    return render(request, 'website/templates/get-question.html', context)
    
# post answer to a question, send notification to the user, whose question is answered
# if anwser is posted by the owner of the question, no notification is sent
@login_required
def question_answer(request,qid):
   
    context = {}
    question = get_object_or_404(Question, id=qid)
   
    if request.method == 'POST':
        form = AnswerQuestionForm(request.POST, request.FILES)
        answers = question.answer_set.all()
        answer = Answer() 
        answer.uid = request.user.id

        if form.is_valid():
            cleaned_data = form.cleaned_data
            body = str(cleaned_data['body'])
            answer.body = body.splitlines()    
            answer.question = question
            answer.body = body.encode('unicode_internal')  
            if ('image' in request.FILES):
                answer.image = request.FILES['image']
            answer.save()

            # if user_id of question not matches to user_id of answer that
            # question , no
            if question.user_id != request.user.id:

                notification = Notification()
                notification.uid = question.user_id
                notification.qid = question.id
                notification.aid = answer.id
                notification.save()

            #Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - Your question has been answered".format(question.category)
            to = [question.user.email,settings.FORUM_NOTIFICATION,]
            url = settings.EMAIL_URL
            message = "  "
            message =""" The following new question has been posted in the FOSSEE Forum: \n\n
                Title: {0} \n
                Category: {1}\n
                Link: {2}\n\n

                Regards,\nFOSSEE Team,\nIIT Bombay.
                """.format(
                question.title,
                question.category,  
                settings.DOMAIN_NAME + '/question/' + str(question.id) + "#answer" + str(answer.id)
            )
            # send_mail(subject, message, sender_email, to, fail_silently=True)

            return HttpResponseRedirect("/question/" + str(question.id))

        else:
            context['form'] = form
            context['question'] = question

    else:
        category = request.GET.get('category')
        form = NewQuestionForm(category=category)
        context['category'] = category
        context['question'] = question

    context['form'] = form
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    context.update(csrf(request))
    return render(request, 'website/templates/get-question.html', context)   


# comments for specific answer and notification is sent to owner of the answer
# notify other users in the comment thread
@login_required
def answer_comment(request):

    context = {}
    
    if request.method == 'POST':

        answer_id = request.POST['answer_id']
        answer = Answer.objects.get(pk=answer_id)
        answers = answer.question.answer_set.all()
        answer_creator = answer.user()
        form = AnswerCommentForm(request.POST)

        if form.is_valid():

            body = str(request.POST['body'])
            comment = AnswerComment()
            comment.uid = request.user.id
            comment.answer = answer
            comment.body = body.encode('unicode_internal')
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
            to = [answer_creator.email, settings.FORUM_NOTIFICATION,]
            url = settings.EMAIL_URL
            message =""" 
                A comment has been posted on your answer. \n\n
                Title: {0}\n
                Category: {1}\n
                Link: {2}\n\n
                Regards,\nFOSSEE Team,\nIIT Bombay.
                """.format(
                answer.question.title,
                answer.question.category,
                settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
            ) 
            send_mail(subject, message, sender_email, to)

            # notifying other users in the comment thread
            uids = answer.answercomment_set.filter(answer=answer).values_list('uid', flat=True)
            answer_comments = answer.answercomment_set.filter(answer=answer)

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
            url = settings.EMAIL_URL
            message ="""
                A reply has been posted on your comment.\n\n
                Title: {0}\n
                Category: {1}\n
                Link: {2}\n\n
                Regards,\nFOSSEE Team,\nIIT Bombay.
                """.format(
                answer.question.title,
                answer.question.category, 
                #question.tutorial, 
                settings.DOMAIN_NAME + '/question/' + str(answer.question.id) + "#answer" + str(answer.id)
            )
            # send_mail(subject, message, sender_email, to)  

            return HttpResponseRedirect("/question/" + str(answer.question.id))

        else:

            context.update({
                'form': form,
                'question': answer.question,
                'answers': answers,
            })
            return render(request, 'website/templates/get-question.html', context)

    context.update(csrf(request))
    context.update({
        'form': form,
        'question': answer.question,
        'answers': answers,
    })
    
    return render(request, 'website/templates/get-question.html', context)

# View used to filter question according to category
def filter(request, category=None, tutorial=None):

    if category and tutorial:
        questions = Question.objects.filter(category__name=category).filter(sub_category=tutorial).filter(is_spam=0).order_by('date_created').reverse()
    elif tutorial is None:
        questions = Question.objects.filter(category__name=category).filter(is_spam=0).order_by('date_created').reverse()

    context = {
        'questions': questions,
        'category': category,
        'tutorial': tutorial,
    }

    if 'qid' in request.GET:
        context['qid']  = int(request.GET['qid'])
        
    return render(request, 'website/templates/filter.html',  context)

# post a new question on to forums, notification is sent to mailing list team@fossee.in
@login_required
def new_question(request):

    context = {}
    user = request.user
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    all_category = FossCategory.objects.all()

    if request.method == 'POST':

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

                if str(question.category) == "Scilab Toolbox":
                    context.update(csrf(request))
                    category = request.POST.get('category', None)
                    tutorial = request.POST.get('tutorial', None)
                    context['category'] = category
                    context['tutorial'] = tutorial
                    context['form'] = form
                    return render(request, 'website/templates/new-question.html', context)

                question.sub_category = ""

            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.views = 1
            question.save()
            question.userViews.add(request.user)
            if str(question.sub_category) == 'None':
                question.sub_category = ""
            if (predict(question.body) == "Spam"):
                question.is_spam = 1

            question.save()
            
            #Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            to = (question.category.email, settings.FORUM_NOTIFICATION)
            url = settings.EMAIL_URL

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
                question.is_spam == 1,
            )
            email = EmailMultiAlternatives(
                subject,'',
                sender_email, to,
                headers={"Content-type":"text/html;charset=iso-8859-1"}
            )
            email.attach_alternative(message, "text/html")
            # email.send(fail_silently=True)

            return HttpResponseRedirect('/question/'+ str(question.id))
    
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
        tutorial = request.GET.get('tutorial')
        form = NewQuestionForm(category=category,tutorial = tutorial)
        context['category'] = category
        context['tutorial'] = tutorial
        
    context['form'] = form   
    context.update(csrf(request))
    return render(request, 'website/templates/new-question.html', context)

# Edit a question on forums, notification is sent to mailing list team@fossee.in
@login_required
def edit_question(request, question_id=None):

    context = {}
    user = request.user
    context['SITE_KEY'] = settings.GOOGLE_RECAPTCHA_SITE_KEY
    all_category = FossCategory.objects.all()
    question = get_object_or_404(Question, id=question_id)

    # To prevent random user from manually entering the link and editing
    if (request.user.id != question.user.id or question.answer_set.count() > 0):
        return HttpResponse("Not authorized to edit question.")

    if request.method == 'POST':

        previous_title = question.title
        form = NewQuestionForm(request.POST, request.FILES, instance=question)
        question.title = '' # To prevent same title error in form
        question.save()

        if form.is_valid():

            cleaned_data = form.cleaned_data
            question.user = request.user
            question.category = cleaned_data['category']
            question.sub_category = cleaned_data['tutorial']

            if ('image' in request.FILES):
                question.image = request.FILES['image']

            if (question.sub_category == "Select a Sub Category"):
                if str(question.category) == "Scilab Toolbox":
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
            question.views = 1
            if str(question.sub_category) == 'None':
                question.sub_category = ""
            if (predict(question.body) == "Spam"):
                question.is_spam = 1

            question.save()

            # Sending email when a new question is asked
            sender_name = "FOSSEE Forums"
            sender_email = settings.SENDER_EMAIL
            subject = "FOSSEE Forums - {0} - New Question".format(question.category)
            to = (question.category.email, settings.FORUM_NOTIFICATION)
            url = settings.EMAIL_URL

            message = """
                The following question has been edited by the user in the FOSSEE Forum: <br>
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
                question.is_spam == 1,
            )
            email = EmailMultiAlternatives(
                subject,'',
                sender_email, to,
                headers={"Content-type":"text/html;charset=iso-8859-1"}
            )
            email.attach_alternative(message, "text/html")
            # email.send(fail_silently=True)

            return HttpResponseRedirect('/question/'+ str(question.id))
    
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

        category = request.GET.get('category')
        tutorial = request.GET.get('tutorial')
        context['category'] = category
        context['tutorial'] = tutorial
        
    context['form'] = form   
    context.update(csrf(request))
    return render(request, 'website/templates/edit-question.html', context)

# View for deleting question, notification is sent to mailing list team@fossee.in
@login_required
def question_delete(request, question_id):

    question = get_object_or_404(Question, id=question_id)
    title = question.title

    # To prevent random user from manually entering the link and deleting
    if (request.user.id != question.user.id or question.answer_set.count() > 0):
        return HttpResponse("Not authorized to delete question.")

    # Sending email when a question is deleted
    sender_name = "FOSSEE Forums"
    sender_email = settings.SENDER_EMAIL
    subject = "FOSSEE Forums - {0} - New Question".format(question.category)
    to = (question.category.email, settings.FORUM_NOTIFICATION)
    url = settings.EMAIL_URL

    message = """
        The following question has been deleted by the user in the FOSSEE Forum: <br>
        <b> Title: </b>{0}<br>
        <b> Category: </b>{1}<br>
        <b> Question : </b>{2}<br>
        """.format(
        title,
        question.category,
        question.body,
    )
    email = EmailMultiAlternatives(
        subject,'',
        sender_email, to,
        headers={"Content-type":"text/html;charset=iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    # email.send(fail_silently=True)

    question.delete()
    return render(request, 'website/templates/question-delete.html', {'title': title})

# return number of votes and initial votes
# user who asked the question,cannot vote his/or anwser, 
# other users can post votes
def vote_post(request):

    post_id = int(request.POST.get('id'))
    
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    question_id =  request.POST.get('id')
    cur_post = get_object_or_404(Question, id=post_id)
    thisuserupvote = cur_post.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = cur_post.userDownVotes.filter(id=request.user.id).count()
    initial_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()

    if request.user.id != cur_post.user_id:
        
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
                # "Error - Unknown vote type or no vote to recall"
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
def ans_vote_post(request):

    
    post_id = int(request.POST.get('id'))
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    answer_id =  request.POST.get('id') 
    cur_post = get_object_or_404(Answer, id=post_id)

    thisuserupvote = cur_post.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = cur_post.userDownVotes.filter(id=request.user.id).count()
    initial_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()

    if request.user.id != cur_post.uid:

        # This condition is for voting
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
            return HttpResponse(initial_votes)

        num_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()
        cur_post.num_votes = num_votes
        cur_post.save()

        return HttpResponse(num_votes)
    
    else:
        return HttpResponse(initial_votes)


# notification if any on header, when user logs in to the account 
@login_required
def user_notifications(request, user_id):

    if str(user_id) == str(request.user.id):

        try :
            notifications = Notification.objects.filter(uid=user_id).order_by('date_created').reverse()
            context = {
                'notifications': notifications,
            }
            return render(request, 'website/templates/notifications.html', context)

        except:
            Notification.objects.filter(uid=request.user.id).delete()
            return HttpResponseRedirect("/user/{0}/notifications/".format(request.user.id))

    else:
        return HttpResponse("Not authorized to view notifications.")


# to clear notification from header, once viewed or cancelled
@login_required
def clear_notifications(request):
    Notification.objects.filter(uid=request.user.id).delete()
    return HttpResponseRedirect("/user/{0}/notifications/".format(request.user.id))

def search(request):
    context = {
        'categories': categories
    }
    return render(request, 'website/templates/search.html', context)

# Ajax Section
# All the ajax views go below
@csrf_exempt
def ajax_category(request):
    context = {
        'categories': categories,
    }
    return render(request, 'website/templates/ajax_tutorials.html', context)

@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':

        category = request.POST.get('category')

        if category == '12':
            tutorials = SubFossCategory.objects.filter(parent_id =category)
            context = {
                'tutorials': tutorials,
            }
            return render(request, 'website/templates/ajax-tutorials.html', context)

        else:
            return HttpResponse("changed")
            pass

@csrf_exempt
def ajax_answer_update(request):
    if request.method == 'POST':
        aid = request.POST['answer_id']
        body = request.POST['answer_body']
        answer= get_object_or_404(Answer, pk=aid)

        if answer:
            if answer.uid == request.user.id or request.user.id in admins:
                answer.body = body.encode('unicode_escape')
                answer.save()

        return HttpResponse("saved")

@csrf_exempt
def ajax_answer_comment_update(request):
    if request.method == "POST":
        comment_id = request.POST["comment_id"]
        comment_body = request.POST["comment_body"]
        comment = get_object_or_404(AnswerComment, pk=comment_id)

        if comment:
            if comment.uid == request.user.id or request.user.id in admins:
                comment.body = comment_body.encode('unicode_escape')
                comment.save()

        return HttpResponse("saved")


@csrf_exempt
def ajax_similar_questions(request):
    if request.method == 'POST':
        category = request.POST['category']
        tutorial = request.POST['tutorial']
        
        # add more filtering when the forum grows
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial)
        context = {
            'questions': questions
        }
        return render(request, 'website/templates/ajax-similar-questions.html', context)

@csrf_exempt
def ajax_notification_remove(request):
    if request.method == "POST":
        nid = request.POST["notification_id"]
        notification = Notification.objects.get(pk=nid)

        if notification:
            if notification.uid == request.user.id:
                notification.delete()
                return HttpResponse("removed")

    return HttpResponse("failed")

@csrf_exempt
def ajax_keyword_search(request):
    if request.method == "POST":
        key = request.POST['key']

        questions = Question.objects.filter(title__contains=key)
        context = {
            'questions': questions
        }

        return render(request, 'website/templates/ajax-keyword-search.html', context)