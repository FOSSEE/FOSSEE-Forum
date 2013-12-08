from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from website.models import Question, Reply, TutorialDetails, TutorialResources
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
    questions = Question.objects.all().order_by('date_created').reverse()[:10]
    context = {
        'questions': questions,
        'user': request.user
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
    return HttpResponseRedirect('/question/'+str(qid))

def filter(request,  category=None, tutorial=None, minute_range=None, second_range=None):
    context = {}
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
        video_info = get_video_info('/home/cheese/test-video.ogv')

        # convert minutes to 1 if less than 0
        # convert seconds to nearest upper 10th number eg(23->30)
        minutes = video_info['minutes']
        seconds = video_info['seconds']
        if minutes < 0: 
            minutes = 1
        seconds = int(seconds - (seconds % 10 - 10))

        print minutes, seconds
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
