from django.shortcuts import render
from website.models import Question, Answer, Notification, \
    AnswerComment, FossCategory, Profile, SubFossCategory, FossCategory
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from graphos.renderers.gchart import PieChart
from graphos.renderers.gchart import LineChart
from graphos.sources.simple import SimpleDataSource
from datetime import datetime, timedelta
from .forms import Category
from django.shortcuts import render, get_object_or_404, \
    render_to_response
from website.helpers import get_video_info, prettify
from website.forms import NewQuestionForm, AnswerQuestionForm, \
    AnswerCommentForm
from django.core.context_processors import csrf
from forums import settings
from django.core.mail import send_mail

@staff_member_required
def home(request):
    question_count = Question.objects.all().count()
    unanswered_quesitons_count = 0
    questions = Question.objects.all()
    for q in questions:
        if q.answer_set.count() == 0:
            unanswered_quesitons_count = unanswered_quesitons_count + 1
    answered_question_count = question_count - unanswered_quesitons_count
    user_count = User.objects.all().count()

    data = [
        ['Questions', 'Answers'],
        ['Answered Questions', answered_question_count],
        ['Unanswered Questions', unanswered_quesitons_count]

    ]

    data_source = SimpleDataSource(data=data)

    chart = PieChart(data_source, height=300, width=796, options={'is3D': False,
                                                                  'title': 'Questions Chart',
                                                                  } )


    data_graph = [['date', 'Users']]

    for days_to_subtract in reversed(range(11)):
        date = datetime.now().date() - timedelta(days=days_to_subtract)
        user_joined =  User.objects.filter(date_joined__lte=date).count()
        data_graph_sub = []
        data_graph_sub = [date,user_joined]
        data_graph.append(data_graph_sub)

    data_graph_source = SimpleDataSource(data=data_graph)

    graph = LineChart(data_graph_source, options={'title': 'Users per day'})

    context = {'chart': chart,
               'graph': graph,
               'question_count': question_count,
               'answered': answered_question_count,
               'unanswered': unanswered_quesitons_count,
               'user_count': user_count
    }

    return render(request, "moderator/templates/index.html", context)



@staff_member_required
def user_info(request):
    """Display the user information"""

    user = User.objects.all().order_by('date_joined').reverse()

    context = {'User': user}
    return render(request, 'moderator/templates/users.html', context)


@csrf_exempt
def user_update(request):
    """To delete or modify the data of user"""

    if request.POST:
        if 'Activate' in request.POST:
            for id in request.POST.getlist('User_id'):
                user = User.objects.get(id=id)
                user.is_active = 1
                user.save()

        if 'Deactivate' in request.POST:
            for id in request.POST.getlist('User_id'):
                user = User.objects.get(id=id)
                user.is_active = 0
                user.save()

        if 'Add in Staff' in request.POST:
            for id in request.POST.getlist('User_id'):
                user = User.objects.get(id=id)
                user.is_staff = 1
                user.save()

        if 'Remove from Staff' in request.POST:
            for id in request.POST.getlist('User_id'):
                if int(id) != int(request.user.id):
                    print request.user.id
                    print id
                    user = User.objects.get(id=id)
                    user.is_staff = 0
                    user.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
