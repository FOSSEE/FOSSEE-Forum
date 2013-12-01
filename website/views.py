from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from website.models import Question, Reply, TutorialDetails, TutorialResources
from website.forms import NewQuestionForm
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
    questions = Question.objects.all()
    context = {
        'questions': questions
    }
    return render_to_response('website/templates/index.html', context)

def get_question(request, question_id=None):
    question = get_object_or_404(Question, id=question_id)
    replies = question.reply_set.all()
    context = {
        'question': question,
        'replies': replies
    }
    return render_to_response('website/templates/get_question.html', context)

def filter(request,  category='', tutorial='', minute_range='', second_range=''):
    res = category + '<br>' + tutorial + '<br>' + minute_range + '<br>' + second_range
    return HttpResponse(res)

@login_required
def new_question(request):
    if request.method == 'POST':
        form = NewQuestionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            question = Question()
            question.user = request.user
            question.category = cleaned_data['category']
            question.tutorial = cleaned_data['tutorial']
            question.minute_range = cleaned_data['minute_range']
            question.second_range = cleaned_data['second_range']
            question.title = cleaned_data['title']
            question.body = cleaned_data['body']
            question.save()
            return HttpResponse('atlast :>')
    else:
        form = NewQuestionForm()

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render_to_response('website/templates/new-question.html', context)

@csrf_exempt
def ajax_tutorials(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        tutorials = TutorialDetails.objects.using('spoken').filter(foss_category=category)
        context = {
            'tutorials': tutorials
        }
        return render_to_response('website/templates/ajax-tutorials.html', context)

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
        return render_to_response('website/templates/ajax-duration.html', context)
