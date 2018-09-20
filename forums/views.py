from builtins import str
from builtins import range
import urllib.parse, urllib.request
import json
import ssl
import random, string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from forums.forms import *
from website.models import *

# to register new user and send confirmation link to registerd email id
def account_register(request):

    context = {}

    if (request.method == 'POST'):

        form = RegisterForm(request.POST)

        if form.is_valid():

            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode('utf-8')
            req = urllib.request.Request(url, data)
            response = urllib.request.urlopen(req)
            result = json.load(response)
            ''' End reCAPTCHA validation '''

            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            user = User.objects.create_user(username, email, password)
            user.is_active = False

            if result['success']:
                user.save()
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')

            confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
            p = Profile(user = user, confirmation_code = confirmation_code)
            p.save()
            send_registration_confirmation(user)
            messages.success(request, """
                Please confirm your registration by clicking on the activation link which has been sent to your registered email id.
            """)

            return render(request, 'forums/templates/message.html')

        context = {
            'form':form,
            'SITE_KEY': settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        return render(request, 'forums/templates/user-register.html', context)

    else:
        form = RegisterForm()
        context = {
            'form': form,
            'SITE_KEY': settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        context.update(csrf(request))
        return render(request, 'forums/templates/user-register.html', context)

# alert user after user account confirmation
def confirm(request, confirmation_code, username):

    try:
        user = User.objects.get(username = username)
        profile = Profile.objects.get(user = user)

        if (profile.confirmation_code == confirmation_code):
            user.is_active = True
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            messages.success(request, "Your account has been activated!. Please update your profile to complete your registration")
            return HttpResponseRedirect('/accounts/profile/')

        else:
            messages.success(request, "Something went wrong!. Please try again!")
            return HttpResponseRedirect('/')

    except Exception as e:
        messages.success(request, "Your account not activated!. Please try again!")
        return HttpResponseRedirect('/')


# add details to the profile table of the user
# update profile after registration confirmation
@login_required
def account_profile(request):

    user = request.user
    try:
        profile = Profile.objects.get(user_id = user.id)
    except:
        profile = Profile(user = user)

    if (request.method == 'POST'):

        form = ProfileForm(user, request.POST)

        if form.is_valid():

            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            profile.address = request.POST['address']
            profile.phone = request.POST['phone']
            user.save()
            form_data = form.save(commit = False)
            form_data.user_id = user.id
            profile.save()

            messages.success(request, "Your profile has been updated!")
            return HttpResponseRedirect("/accounts/view-profile/{0}/".format(user.id))

        # return account_view_profile(request, user.id)
        context = {'form':form}
        return render(request, 'forums/templates/profile.html', context)

    else:
        context = {}
        context.update(csrf(request))
        instance = profile
        context['form'] = ProfileForm(user, instance = instance)
        return render(request, 'forums/templates/profile.html', context)

# view all profile details saved for the user, when clicked on my profile
@login_required
def account_view_profile(request, user_id):

    user = User.objects.get(pk = user_id)
    try:
        profile = Profile.objects.get(user = user)
    except:
        profile = Profile(user = user)
    flag = False

    questions = Question.objects.filter(user_id = user_id).order_by('date_created').reverse()
    answers = Answer.objects.filter(uid = user_id).order_by('date_created').reverse()
    form = ProfileForm(user, instance = profile)

    if str(user_id) == str(request.user.id):
        flag = True

    context = {
        'show': flag,
        'profile' : profile,
        'questions' : questions,
        'answers' : answers,
        'form' : form,
    }
    return render(request, 'forums/templates/view-profile.html', context)

# send confirm registration link
def send_registration_confirmation(user):

    p = Profile.objects.get(user = user)

    # Sending email when an answer is posted
    subject = 'Account Active Notification'
    message = """Dear {0}, \n
    Thank you for registering at {1}.\n\n You may activate your account by clicking on this link or copying and pasting it in your browser
    {2}\n
    Regards, \n
    FOSSEE forum\n
    IIT Bombay.
    """.format(
        user.username,
        settings.DOMAIN_NAME,
        settings.DOMAIN_NAME + "/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
    )
    email = EmailMultiAlternatives(
        subject, message, settings.SENDER_EMAIL,
        to = [user.email], bcc = [], cc = [settings.FORUM_NOTIFICATION],
        headers = {'Reply-To': settings.SENDER_EMAIL, "Content-type":"text/html;charset = iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    try:
        result = email.send(fail_silently = False)
    except:
        pass

# user login        
def user_login(request):

    if request.user.is_anonymous:

        if (request.method == 'POST'):
            form = UserLoginForm(request.POST)

            # Valid credentials are entered
            if form.is_valid():
                
                cleaned_data = form.cleaned_data
                user = cleaned_data.get("user")
                login(request, user)

                if ('next' in request.POST):
                    next_url = request.POST.get('next')
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect('/')
            
            # Invalid credentials entered
            else:
                next_url = request.POST.get('next')
                context = {
                    'form': form, 
                    'next': next_url, 
                }
                context.update(csrf(request))
                return render(request, 'forums/templates/user-login.html', context)
                
        else:
            form = UserLoginForm()
        
        next_url = request.GET.get('next')
        context = {
            'form': form, 
            'next': next_url, 
        }
        context.update(csrf(request))
        return render(request, 'forums/templates/user-login.html', context)

    else:
        return HttpResponseRedirect('/')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')