import re
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404,render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

from website.models import Question, Answer, Notification, AnswerComment, FossCategory
from spoken_auth.models import TutorialDetails, TutorialResources
from website.forms import NewQuestionForm, AnswerQuestionForm,AnswerCommentForm
from website.helpers import get_video_info, prettify
from django.db.models import Count


admins = (
   9, 4376, 4915, 14595, 12329, 22467, 5518, 30705
)
categories = FossCategory.objects.order_by('name')

def home(request):
    questions = Question.objects.all().order_by('date_created').reverse()[:10]
    context = {
        'categories': categories,
        'questions': questions
    }
    return render(request, "website/templates/index.html", context)

def questions(request):
    questions = Question.objects.all().order_by('date_created').reverse()
    paginator = Paginator(questions, 20)
    page = request.GET.get('page')
    for q in questions:
    	print q.title
    	print q.num_votes
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)
    context = {
        'questions': questions
    }
    
    return render(request, 'website/templates/questions.html', context)

def get_question(request, question_id=None, pretty_url=None):
    question = get_object_or_404(Question, id=question_id)
    pretty_title = prettify(question.title)
    if pretty_url != pretty_title:
        return HttpResponseRedirect('/question/'+ question_id + '/' + pretty_title)
    answers = question.answer_set.all()
    form = AnswerQuestionForm()
    thisuserupvote = question.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = question.userDownVotes.filter(id=request.user.id).count()
    net_count = question.userUpVotes.count() - question.userDownVotes.count()
    
    context = {
        'question': question,
        'answers': answers,
        'form': form,
        'thisUserUpvote': thisuserupvote,
        'thisUserDownvote': thisuserdownvote,
        'net_count': net_count,
        'num_votes':question.num_votes
    }
    context.update(csrf(request))
    # updating views count
    question.views += 1
    question.save()
   
    return render(request, 'website/templates/get-question.html', context)

@login_required
def question_answer(request,qid):
   
    dict_context = {}
   
    if request.method == 'POST':
    	
        form = AnswerQuestionForm(request.POST)
	question = get_object_or_404(Question, id=qid)
        answers = question.answer_set.all()
        answer = Answer()
        
        answer.uid = request.user.id
        if form.is_valid():
            cleaned_data = form.cleaned_data
            qid = cleaned_data['question']
            body = cleaned_data['body']
            answer.question = question
            answer.body = body.encode('unicode_escape')
            answer.save()
            # if user_id of question not matches to user_id of answer that
            # question , no
            if question.user_id != request.user.id:
                notification = Notification()
                notification.uid = question.user_id
                notification.pid = request.user.id
                notification.qid = qid
                notification.aid = answer.id
                notification.save()
                
                user = User.objects.get(id=question.user_id)
                # Sending email when an answer is posted
                subject = 'Question has been answered'
                message = """
                    Dear {0}<br><br>
                    Your question titled <b>"{1}"</b> has been answered.<br>
                    Link: {2}<br><br>
                    Regards,<br>
                    Fossee Forums
                """.format(
                    user.username, 
                    question.title, 
                    'http://forums.fossee.in/question/' + str(question.id) + "#answer" + str(answer.id)
                )
                
                email = EmailMultiAlternatives(
                    subject,'', 'forums', 
                    [user.email],
                    headers={"Content-type":"text/html;charset=iso-8859-1"}
                )
                
                email.attach_alternative(message, "text/html")
                email.send(fail_silently=True)
                # End of email send
	    return HttpResponseRedirect('/question/'+ str(qid) + "#answer" + str(answer.id)) 
	else:
		dict_context  = {
			'question':question,
			'answers': answers,
			'form': form
		}
		
	    	return render(request, 'website/templates/get-question.html', dict_context)
	
    return HttpResponseRedirect('/') 
        
    

@login_required
def answer_comment(request):
	if request.method == 'POST':
		answer_id = request.POST['answer_id'];
		answer = Answer.objects.get(pk=answer_id)
		answers = answer.question.answer_set.all()
		form = AnswerCommentForm(request.POST)
		if form.is_valid():
			body = request.POST['body']
			comment = AnswerComment()
			comment.uid = request.user.id
			comment.answer = answer
			comment.body = body.encode('unicode_escape')
			
			comment.save()
		  	# notifying the answer owner
		  	
			if answer.uid != request.user.id:
			    notification = Notification()
			    notification.uid = answer.uid
			    notification.pid = request.user.id
			    notification.qid = answer.question.id
			    notification.aid = answer.id
			    notification.cid = comment.id
			    notification.save()
			    
			    user = User.objects.get(id=answer.uid)
			    subject = 'Comment for your answer'
			    message = """
				Dear {0}<br><br>
				A comment has been posted on your answer.<br>
				Link: {1}<br><br>
				Regards,<br>
				FOSSEE Forums
			    """.format(
				user.username,
				"http://forums.fossee.in/question/" + str(answer.question.id) + "#answer" + str(answer.id)
			    )
			    forums_mail(user.email, subject, message)
		  	# notifying other users in the comment thread
			uids = answer.answercomment_set.filter(answer=answer).values_list('uid', flat=True)
			#getting distinct uids
			uids = set(uids) 
			uids.remove(request.user.id)
			for uid in uids:
			    notification = Notification()
			    notification.uid = uid
			    notification.pid = request.user.id
			    notification.qid = answer.question.id
			    notification.aid = answer.id
			    notification.cid = comment.id
			    notification.save()
			    
			    user = User.objects.get(id=uid)
			    subject = 'Comment has a reply'
			    message = """
				Dear {0}<br><br>
				A reply has been posted on your comment.<br>
				Link: {1}<br><br>
				Regards,<br>
				FOSSEE Forums
			    """.format(
				user.username,
				"http://forums.fossee.in/question/" + str(answer.question.id) + "#answer" + str(answer.id)
			    )
			    forums_mail(user.email, subject, message)

    			return HttpResponseRedirect("/question/" + str(answer.question.id))
	context = {}
    	context.update(csrf(request))
    	context.update({'form':form,
	'question':answer.question,
	'answers':answers})
        return render(request, 'website/templates/get-question.html', context)


def filter(request,  category=None, tutorial=None, minute_range=None, second_range=None):
    dict_context = {}
    context = {
        'category': category,
        'tutorial': tutorial,
        'minute_range': minute_range,
        'second_range': second_range
    }

    if category and tutorial and minute_range and second_range:
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial).filter(minute_range=minute_range).filter(second_range=second_range)
    elif tutorial is None:
        questions = Question.objects.filter(category__name=category)
    elif minute_range is None:
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial)
    else:  #second_range is None
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial).filter(minute_range=minute_range)

    if 'qid' in request.GET:
        context['qid']  = int(request.GET['qid'])
     
    categories = FossCategory.objects.filter(name=category)
        
    dict_context = {
			'questions':questions,
			'categories': categories
		   }
		
    return render(request, 'website/templates/filter.html',  dict_context)

@login_required
def new_question(request):
    context = {}
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        if form.is_valid():
           
            cleaned_data = form.cleaned_data
            question = Question()
            question.user = request.user
            question.category = cleaned_data['category']
            question.title = cleaned_data['title']
            question.body = cleaned_data['body'].encode('unicode_escape')
            question.views= 1 
            question.save()
           
            #Sending email when a new question is asked
            subject = 'New Forum Question'
            message = """
                The following new question has been posted in the FOSSEE Forum: <br>
                Title: <b>{0}</b><br>
                Category: <b>{1}</b><br>
                
                Link: <a href="{2}">{2}</a><br>
            """.format(
                question.title,
                question.category, 
                #question.tutorial, 
                'http://forums.fossee.in/question/'+str(question.id)
            )
            email = EmailMultiAlternatives(
                subject,'', 'forums', 
                ['team@fossee.in'],
                headers={"Content-type":"text/html;charset=iso-8859-1"}
            )
           
            email.attach_alternative(message, "text/html")
            email.send(fail_silently=True)
            
            return HttpResponseRedirect('/')
    else:
       
        category = request.GET.get('category')
        form = NewQuestionForm(category=category)
        context['category'] = category
    
    context['form'] = form
   
    context.update(csrf(request))
    return render(request, 'website/templates/new-question.html', context)

  
def vote_post(request):

    
    post_id = int(request.POST.get('id'))
    
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    
    cur_post = get_object_or_404(Question, id=post_id)

    thisuserupvote = cur_post.userUpVotes.filter(id=request.user.id).count()
    thisuserdownvote = cur_post.userDownVotes.filter(id=request.user.id).count()

    initial_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()

    # print "User Initial Upvote and Downvote: %d %d %s " % (thisuserupvote, thisuserdownvote, vote_action)

    #This loop is for voting
    if vote_action == 'vote':
        if (thisuserupvote == 0) and (thisuserdownvote == 0):
            if vote_type == 'up':
                cur_post.userUpVotes.add(request.user)
            elif vote_type == 'down':
                cur_post.userDownVotes.add(request.user)
            else:
                return HttpResponse("Error: Unknown vote-type passed.")
        else:
            return HttpResponse(initial_votes)
    #This loop is for canceling vote
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
   
    print "Num Votes: %s" % num_votes

    return HttpResponse(num_votes)

def ans_vote_post(request):

    
    post_id = int(request.POST.get('id'))
    
    vote_type = request.POST.get('type')
    vote_action = request.POST.get('action')
    
    cur_post = get_object_or_404(Answer, id=post_id)

    userupvote = cur_post.userUpVotes.filter(id=request.user.id).count()
    userdownvote = cur_post.userDownVotes.filter(id=request.user.id).count()

    initial_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()

    # print "User Initial Upvote and Downvote: %d %d %s " % (thisuserupvote, thisuserdownvote, vote_action)

    #This loop is for voting
    if vote_action == 'vote':
        if (userupvote == 0) and (userdownvote == 0):
            if vote_type == 'up':
                cur_post.userUpVotes.add(request.user)
            elif vote_type == 'down':
                cur_post.userDownVotes.add(request.user)
            else:
                return HttpResponse("Error: Unknown vote-type passed.")
        else:
            return HttpResponse(initial_votes)
    #This loop is for canceling vote
    elif vote_action == 'recall-vote':
        if (vote_type == 'up') and (userupvote == 1):
            cur_post.userUpVotes.remove(request.user)
        elif (vote_type == 'down') and (userdownvote == 1):
            cur_post.userDownVotes.remove(request.user)
        else:
            # "Error - Unknown vote type or no vote to recall"
            return HttpResponse(initial_votes)
    else:
        return HttpResponse("Error: Bad Action.")

    num_votes = cur_post.userUpVotes.count() - cur_post.userDownVotes.count()
    cur_post.num_votes = num_votes
    cur_post.save()
   
    print "Num Votes: %s" % num_votes

    return HttpResponse(num_votes)

# Notification Section
@login_required
def user_questions(request, user_id):
    
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    if str(user_id) == str(request.user.id):
        total = Question.objects.filter(user_id=user_id).count()
        total = int(total - (total % 10 - 10))
        questions = Question.objects.filter(user_id=user_id).order_by('date_created').reverse()[marker:marker+10]
        
        context = {
            'questions': questions,
            'total': total,
            'marker': marker
        }
       
        return render(request, 'website/templates/user-questions.html', context)
    return HttpResponse("go away")

@login_required
def user_answers(request, user_id):
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    if str(user_id) == str(request.user.id):
        total = Answer.objects.filter(uid=user_id).count()
        total = int(total - (total % 10 - 10))
        answers =Answer.objects.filter(uid=user_id).order_by('date_created').reverse()[marker:marker+10]
        context = {
            'answers': answers,
            'total': total,
            'marker': marker
        }
        print "anwer_total"
        print total
        return render(request, 'website/templates/user-answers.html', context)
    return HttpResponse("go away")

@login_required
def user_notifications(request, user_id):
    print "user_id"
    print user_id
    print request.user.id
    if str(user_id) == str(request.user.id):
        notifications = Notification.objects.filter(uid=user_id).order_by('date_created').reverse()
        context = {
            'notifications': notifications
        }
        
        return render(request, 'website/templates/notifications.html', context)
    return HttpResponse("go away ...")

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
        'categories': categories
    }
    return render(request, 'website/templates/ajax_categories.html', context)

@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        tutorials = TutorialDetails.objects.using('spoken').filter(foss__foss=category)
        context = {
            'tutorials': tutorials
        }
        return render(request, 'website/templates/ajax-tutorials.html', context)

@csrf_exempt
def ajax_duration(request):
    if request.method == 'POST':
        category = request.POST['category']
        tutorial =request.POST['tutorial']
        video_detail = TutorialDetails.objects.using('spoken').get(
            Q(foss__foss=category),
            Q(tutorial=tutorial)
        )
        video_resource = TutorialResources.objects.using('spoken').get(
            Q(tutorial_detail_id=video_detail.id),
            Q(language__name='English')
        )
        video_path = '/home/sanmugam/devel/spoken/media/videos/{0}/{1}/{2}'.format(
           str(video_detail.foss_id),
           str(video_detail.id),
           video_resource.video
        )
        # video_path = '/home/cheese/test-video.ogv'
        video_info = get_video_info(video_path)
        
        # convert minutes to 1 if less than 0
        # convert seconds to nearest upper 10th number eg(23->30)
        minutes = video_info['minutes']
        seconds = video_info['seconds']
        if minutes < 0: 
            minutes = 1
        seconds = int(seconds - (seconds % 10 - 10))
        seconds = 60
        context = {
            'minutes': minutes,
            'seconds':seconds,
        }
        return render(request, 'website/templates/ajax-duration.html', context)

@csrf_exempt
def ajax_question_update(request):
    if request.method == 'POST':
        qid = request.POST['question_id']
        title = request.POST['question_title']
        body = request.POST['question_body']
        question = get_object_or_404(Question, pk=qid)
        if question:
            if question.uid == request.user.id or request.user.id in admins:
                question.title = title
                question.body = body.encode('unicode_escape')
                question.save()
        return HttpResponse("saved")

@csrf_exempt
def ajax_details_update(request):
    if request.method == 'POST':
        qid = request.POST['qid']
        category = request.POST['category']
        tutorial = request.POST['tutorial']
        minute_range = request.POST['minute_range']
        second_range = request.POST['second_range']
        question = get_object_or_404(Question, pk=qid)
        if question:
            if question.uid == request.user.id or request.user.id in admins:
                question.category = category
                question.tutorial = tutorial
                question.minute_range = minute_range
                question.second_range = second_range
                question.save()
            return HttpResponse("saved")

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
        minute_range = request.POST['minute_range']
        second_range = request.POST['second_range']
        
        # add more filtering when the forum grows
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial)
        context = {
            'questions': questions
        }
        return render(request, 'website/templates/ajax-similar-questions.html', context);

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

@csrf_exempt
def ajax_time_search(request):
    if request.method == "POST":
        category = request.POST.get('category')
        tutorial = request.POST.get('tutorial')
        minute_range= request.POST.get('minute_range')
        second_range = request.POST.get('second_range')
        questions = None
        print request.POST, "***********"
        if category:
            questions = Question.objects.filter(category=category.replace(' ', '-'))
            print "sssssssssss", questions
        if tutorial:
            questions = questions.filter(tutorial=tutorial.replace(' ', '-'))
        if minute_range:
            questions = questions.filter(category=category.replace(' ', '-'), tutorial=tutorial.replace(' ', '-'), minute_range=minute_range)
        if second_range:
            questions = questions.filter(category=category.replace(' ', '-'), tutorial=tutorial.replace(' ', '-'),second_range=second_range)
        print questions, "&&&&&&&&&&&"
        context = {
            'questions': questions
        }
        return render(request, 'website/templates/ajax-time-search.html', context)

@csrf_exempt
def ajax_vote(request):
    #for future use
    pass

def forums_mail(to = '', subject='', message=''):
    # Start of email send
    email = EmailMultiAlternatives(
        subject,'', 'forums', 
        to.split(','),
        headers={"Content-type":"text/html;charset=iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    email.send(fail_silently=True)
    # End of email send

# daily notifications for unanswered questions.
def unanswered_notification(request):
    questions = Question.objects.all()
    total_count = 0
    message = """ 
        The following questions are left unanswered.
        Please take a look at them. <br><br>
    """
    for question in questions:
        if not question.answer_set.count():
            total_count += 1
            message += """ 
                #{0}<br>
                Title: <b>{1}</b><br>
                Category: <b>{2}</b><br>
                Link: <b>{3}</b><br>
                <hr>
            """.format(
                total_count,
                question.title,
                question.category,
                'http://forums.fossee.in/question/' + str(question.id)
            )
    to = "team@fossee.in"
    subject = "Unanswered questions in the forums."
    if total_count:
        forums_mail(to, subject, message)
    return HttpResponse(message)

