import re

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail

from website.models import Question, Reply, Notification, TutorialDetails, TutorialResources
from website.forms import NewQuestionForm, ReplyQuesitionForm
from website.helpers import get_video_info


categories = [
    'Advanced-C++', 'BASH', 'Blender', 
    'C-and-C++', 'CellDesigner', 'Digital-Divide', 
    'Drupal', 'Firefox', 'GChemPaint', 'Geogebra', 
    'GeoGebra-for-Engineering-drawing', 'GIMP', 'GNS3', 
    'GSchem', 'Java', 'Java-Business-Application', 
    'KiCad', 'KTouch', 'KTurtle', 'LaTeX', 
    'LibreOffice-Suite-Base', 'LibreOffice-Suite-Calc', 
    'LibreOffice-Suite-Draw', 'LibreOffice-Suite-Impress', 
    'LibreOffice-Suite-Math', 'LibreOffice-Suite-Writer', 
    'Linux', 'Netbeans', 'Ngspice', 'OpenFOAM', 'Orca', 
    'PERL', 'PHP-and-MySQL', 'Python', 'Python-Old-Version', 
    'QCad', 'R', 'Ruby', 'Scilab', 'Selenium', 
    'Single-Board-Heater-System', 'Spoken-Tutorial-Technology', 
    'Step', 'Thunderbird', 'Tux-Typing', 'What-is-Spoken-Tutorial', 'Xfig'
] 

def home(request):
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    total = Question.objects.all().count()
    total = int(total - (total % 10 - 10))
    questions = Question.objects.all().order_by('date_created').reverse()[marker:marker+10]
    context = {
        'questions': questions,
        'total': total,
        'marker': marker
    }
    return render(request, 'website/templates/index.html', context)

def get_question(request, question_id=None):
    question = get_object_or_404(Question, id=question_id)
    replies = question.reply_set.all()
    form = ReplyQuesitionForm()
    context = {
        'question': question,
        'replies': replies,
        'form': form
    }
    context.update(csrf(request))
    # updating views count
    question.views += 1
    question.save()
    return render(request, 'website/templates/get-question.html', context)

@login_required
def question_reply(request):
    if request.method == 'POST':
        form = ReplyQuesitionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            qid = cleaned_data['question']
            body = cleaned_data['body']
            question = get_object_or_404(Question, id=qid)
            reply = Reply()
            reply.uid = request.user.id
            reply.question = question
            reply.body = body
            reply.save()
            if question.uid != request.user.id:
                notification = Notification()
                notification.uid = question.uid
                notification.pid = request.user.id
                notification.qid = qid
                notification.rid = reply.id
                notification.save()
    return HttpResponseRedirect('/question/'+str(qid))

def filter(request,  category=None, tutorial=None, minute_range=None, second_range=None):
    context = {
        'category': category,
        'tutorial': tutorial,
        'minute_range': minute_range,
        'second_range': second_range
    }
    if category and tutorial and minute_range and second_range:
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial).filter(minute_range=minute_range).filter(second_range=second_range)
    elif tutorial is None:
        questions = Question.objects.filter(category=category)
    elif minute_range is None:
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial)
    else:  #second_range is None
        questions = Question.objects.filter(category=category).filter(tutorial=tutorial).filter(minute_range=minute_range)

    if 'qid' in request.GET:
        qid = request.GET['qid']
        question = get_object_or_404(Question, id=qid)
        context['question'] = question
        questions = questions.filter(~Q(id=qid))

    context['questions'] = questions
    return render(request, 'website/templates/filter.html', context)

@login_required
def new_question(request):
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            question = Question()
            question.uid = request.user.id
            question.category = cleaned_data['category']
            question.tutorial = cleaned_data['tutorial']
            question.minute_range = cleaned_data['minute_range']
            question.second_range = cleaned_data['second_range']
            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.views= 1 
            question.save()
            return HttpResponseRedirect('/')
    else:
        form = NewQuestionForm()

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'website/templates/new-question.html', context)

@login_required
def user_questions(request, user_id):
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    if str(user_id) == str(request.user.id):
        total = Question.objects.filter(uid=user_id).count()
        total = int(total - (total % 10 - 10))
        questions = Question.objects.filter(uid=user_id).order_by('date_created').reverse()[marker:marker+10]

        context = {
            'questions': questions,
            'total': total,
            'marker': marker
        }
        return render(request, 'website/templates/user-questions.html', context)
    return HttpResponse("go away")

@login_required
def user_replies(request, user_id):
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    if str(user_id) == str(request.user.id):
        total = Reply.objects.filter(uid=user_id).count()
        total = int(total - (total % 10 - 10))
        replies =Reply.objects.filter(uid=user_id).order_by('date_created').reverse()[marker:marker+10]
        context = {
            'replies': replies,
            'total': total,
            'marker': marker
        }
        return render(request, 'website/templates/user-replies.html', context)
    return HttpResponse("go away")

@login_required
def user_notifications(request, user_id):
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
    return HttpResponseRedirect("/user/{}/notifications/".format(request.user.id))

def search(request):
    context = {
        'categories': categories
    }
    return render(request, 'website/templates/search.html', context)

# Ajax Section
# All the ajax views go below
@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        tutorials = TutorialDetails.objects.using('spoken').filter(foss_category=category)
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
            Q(foss_category=category),
            Q(tutorial_name=tutorial)
        )
        video_resource = TutorialResources.objects.using('spoken').get(
            Q(tutorial_detail_id=video_detail.id),
            Q(language='English')
        )
        video_path = '/Sites/spoken_tutorial_org/sites/default/files/{0}'.format(
            video_resource.tutorial_video
        )
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
        body = request.POST['question_body']
        question = get_object_or_404(Question, pk=qid)
        if question:
            if question.uid == request.user.id:
                question.body = body
                question.save()
        return HttpResponse("saved")

@csrf_exempt
def ajax_reply_update(request):
    if request.method == 'POST':
        rid = request.POST['reply_id']
        body = request.POST['reply_body']
        reply= get_object_or_404(Reply, pk=rid)
        if reply:
            if reply.uid == request.user.id:
                reply.body = body
                reply.save()
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
        questions = Question.objects.filter(title__icontains=key)
        context = {
            'questions': questions
        }
        return render(request, 'website/templates/ajax-keyword-search.html', context)

@csrf_exempt
def ajax_time_search(request):
    if request.method == "POST":
        key = request.POST['key']
        questions = Question.objects.filter(title__icontains=key)
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
        
        if category != 'None':
            questions = Question.objects.filter(category=category)
        
        if tutorial != 'None':
            questions = questions.filter(tutorial=tutorial)

        if minute_range != 'None':
            questions = questions.filter(minute_range=minute_range)

        if second_range != 'None':
            questions = questions.filter(second_range=second_range)

        context = {
            'questions': questions
        }

        return render(request, 'website/templates/ajax-time-search.html', context)

def test(request):
    subject = 'New Forum Question'
    message = """
        A new question has been posted in the Spoken-Tutorial Forum. <br>
        Category: OpenFOAM <br>
        Tutorial: Tokens <br>
        <a href="http://google.com" target="_blank">http://google.com</a> <br>
    """
    send_mail(subject, message, 'forums', ['rush2jrp@gmail.com'], 
    headers={"Content-type":"text/html;charset=iso-8859-1"}, fail_silently=True)
    return HttpResponse("done")
