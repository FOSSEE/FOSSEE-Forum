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
from forms import Category, Emails
from django.shortcuts import render, get_object_or_404, \
    render_to_response
from website.helpers import get_video_info, prettify

from django.core.context_processors import csrf
from forums import settings
from django.core.mail import send_mail
from models import NotificationEmail
from moderator.util import delete_question_util, delete_answer_util,\
    delete_comment_util


def get_emails():
    emails = NotificationEmail.objects.all()
    to_list = []
    for email in emails:
        to_list.append(email.email)

    return to_list


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


@staff_member_required
def category(request):
    """Display the various categories and their information"""

    category = FossCategory.objects.all().order_by('date_created'
            ).reverse()

    context = {'FossCategory': category}
    return render(request, 'moderator/templates/category.html', context)


@csrf_exempt
@staff_member_required
def category_form(request, category_id=0):
    """Display and recieve form for editing a category"""

    instance = FossCategory.objects.get(id=category_id)
    context = {}
    if request.method == 'GET':

        form = Category(instance=instance)

        context = {'form': form}

        return render(request, 'moderator/templates/category-form.html',
                      context)
    else:

        if request.FILES:

            form = Category(request.POST, request.FILES,
                            instance=instance)

            if form.is_valid():

                cleaned_data = form.cleaned_data
                image = request.FILES['category_image']
                name = cleaned_data['name']

                form.save()
            else:

                context['form'] = form
                context.update(csrf(request))
                return render(request,
                              'moderator/templates/category-form.html',
                              context)
        else:
            form = Category(request.POST, instance=instance)
            if form.is_valid():
                form.save()
            else:

                context['form'] = form
                context.update(csrf(request))

                return render(request,
                              'moderator/templates/category-form.html',
                              context)

        return HttpResponseRedirect('/moderator/category')


@csrf_exempt
@staff_member_required
def new_category(request):
    """Display and recieve form for new category and store data into database"""

    if request.method == 'GET':
        form = Category()
        context = {}
        context = {'form': form}

        return render(request, 'moderator/templates/category-form.html'
                      , context)
    else:

        form = Category(request.POST, request.FILES)
        if form.is_valid():

            cleaned_data = form.cleaned_data
            image = request.FILES['category_image']
            name = cleaned_data['name']
            image.rename(name + '.jpg')

            form.save()
            return HttpResponseRedirect('/moderator/category')
        else:
            return HttpResponseRedirect('/moderator/category')


@staff_member_required
def questions(request):
    questions = Question.objects.all().order_by('date_created'
            ).reverse()
    context = {'questions': questions}
    return render(request, 'moderator/templates/questions.html',
                  context)


@csrf_exempt
@staff_member_required
def delete_question(request):
    """To delete the questions or questions selected

    the moderator may choose to  one or more question """

    # get list of all question id from post request
    for ques_id in request.POST.getlist('Question_id'):

        # delete all answers of the questions

        (question_title, user_email) = delete_question_util(ques_id)
        Subject = 'Question Deletion Notification'
        sender_email = settings.EMAIL_HOST_USER
        to = get_emails()
        to.extend([request.user.email, user_email])
        to = set(to)
        to = list(to)

        message = \
            """Sir/Madam ,

                Following Question has been deleted from database of FOSSEE Forum
                Title: {0}
                By: {1}
                On: {2}

                """.format(question_title,
                request.user.username, datetime.now())

        send_mail(Subject, message, sender_email, to,
                  fail_silently=False)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
@staff_member_required
def get_question(request, question_id, pretty_url=None):
    if request.method == 'GET':
        question = get_object_or_404(Question, id=question_id)
        sub_category = True
        if question.sub_category == '' or str(question.sub_category) \
            == 'None':
            sub_category = False
        else:
            sub_category = True
        pretty_title = prettify(question.title)

        answers = question.answer_set.all()
        ans_count = question.answer_set.count()

        context = {
            'ans_count': ans_count,
            'question': question,
            'sub_category': sub_category,
            'main_list': answers,
            }

        context.update(csrf(request))

        # updating views count

        question.save()

        return render(request, 'moderator/templates/get-question.html',
                      context)
    else:
        if 'Whole' in request.POST:

            # delete complete question

            question_title = delete_question_util(question_id)
            Subject = 'Question Deletion Notification'
            sender_email = settings.EMAIL_HOST_USER
            to = [request.user.email]

            message = \
                """Sir/Madam ,

                Following Question has been deleted from database of FOSSEE Forum
                Title: {0}
                By: {1}
                On: {2}


                """.format(question_title,
                    request.user.username, datetime.now())

            send_mail(Subject, message, sender_email, to,
                      fail_silently=False)

            return HttpResponseRedirect('/moderator/questions')
        else:

            # delete comments first

            for comment_id in request.POST.getlist('AnswerComment'):
                body = delete_comment_util(comment_id)
                Subject = 'Question Deletion Notification'
                sender_email = settings.EMAIL_HOST_USER
                to = [request.user.email]

                message = \
                    """Sir/Madam ,

                    Following comment has been deleted from database of FOSSEE Forum
                    Comment: {0}
                    By: {1}
                    On: {2}


                    """.format(body,
                        request.user.username, datetime.now())

                send_mail(Subject, message, sender_email, to,
                          fail_silently=False)
            for answer_id in request.POST.getlist('Answer'):
                ans_body = delete_answer_util(answer_id)
                Subject = 'Question Deletion Notification'
                sender_email = settings.EMAIL_HOST_USER
                to = [request.user.email]

                message = \
                    """Sir/Madam ,

                    Following answer has been deleted from database of FOSSEE Forum
                    Answer: {0}
                    By: {1}
                    On: {2}

                    """.format(ans_body,
                        request.user.username, datetime.now())

                send_mail(Subject, message, sender_email, to,
                          fail_silently=False)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'
                    , '/'))


@staff_member_required
def unanswered_questions(request):
    question = Question.objects.all().order_by('date_created').reverse()
    Unanswered = []
    for q in question:
        if q.answer_set.count() == 0:
            Unanswered.append(q)
    context = {'questions': Unanswered}
    return render(request,
                  'moderator/templates/unanswered_questions.html',
                  context)


@csrf_exempt
@staff_member_required
def notification_email(request):
    if request.method == 'GET':

        notification_emails = NotificationEmail.objects.all()

        context = {'notification_emails': notification_emails}
        return render(request,
                      'moderator/templates/notification_email.html',
                      context)
    else:

        ids = request.POST.getlist('id')
        for id in ids:
            if int(id) != 1:
                email = NotificationEmail.objects.filter(id=id)
                email.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'
                                    ))


@csrf_exempt
@staff_member_required
def change_email(request, id):

    instance = get_object_or_404(NotificationEmail, id=id)
    message = ''
    context = {}
    if request.method == 'GET':

        if int(id) == 1:

            if NotificationEmail.objects.get(id=id).email \
                == request.user.email:
                form = Emails(instance=instance)
                context = {'form': form}
            else:
                message = "You can't edit the information of admin"
                context1 = {'message': message}
                return render(request,
                              'moderator/templates/change_email.html',
                              context1)
        else:

            form = Emails(instance=instance)
            context = {'form': form}

        return render(request, 'moderator/templates/change_email.html',
                      context)
    else:
        form = Emails(request.POST, instance=instance)
        if form.is_valid():

            form.save()

            return HttpResponseRedirect('/moderator/notification_email')
        else:

            context['form'] = form
            context.update(csrf(request))

            return render(request,
                          'moderator/templates/change_email.html',
                          context)


@csrf_exempt
@staff_member_required
def new_email(request):

    context = {}
    if request.method == 'GET':
        form = Emails()
        context = {'form': form}
    else:

        form = Emails(request.POST)
        if form.is_valid():

            form.save()

            return HttpResponseRedirect('/moderator/notification_email')
        else:

            context['form'] = form
    context.update(csrf(request))

    return render(request, 'moderator/templates/change_email.html',
                  context)
