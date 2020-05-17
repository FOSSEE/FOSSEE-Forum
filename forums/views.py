# standard library
import json
import random
import ssl
import string
import urllib.parse
import urllib.request
from builtins import range, str

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import Resolver404, resolve
from django.utils.html import strip_tags

# local Django
from website.models import Answer, ModeratorGroup, Profile, Question
from .forms import ProfileForm, RegisterForm, UserLoginForm


# NON-VIEWS FUNCTIONS

def send_registration_confirmation(user):
    """Send Confirmation link to user's registered email id."""
    profile = Profile.objects.get(user=user)

    # Sending email when an answer is posted
    subject = 'Account Activation Notification'
    html_message = render_to_string('forums/templates/account_activation_email.html', {
        'username': user.username,
        'domain': settings.DOMAIN_NAME,
        'link': settings.DOMAIN_NAME + "/accounts/confirm/"\
                + str(profile.confirmation_code) + "/" + user.username,
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.SENDER_EMAIL,
        to=[user.email],
        cc=[settings.FORUM_NOTIFICATION],
        headers={'Reply-To': settings.SENDER_EMAIL,
                 "Content-type":"text/html;charset = iso-8859-1"},
    )
    email.attach_alternative(html_message, "text/html")
    try:
        email.send(fail_silently=False)
    except:
        pass


# VIEWS FUNCTIONS

def user_login(request):
    """Log in the User."""
    if request.user.is_anonymous:
        if request.method == 'POST':
            form = UserLoginForm(request.POST)
            if form.is_valid():
                # Valid credentials are entered
                cleaned_data = form.cleaned_data
                user = cleaned_data.get("user")
                login(request, user)

                # Session Variable created to store if Moderator is using Forum
                # Becomes True only if moderator_home view (website.views) is accessed by user.
                request.session['MODERATOR_ACTIVATED'] = False

                if 'next' in request.POST:
                    next_url = request.POST.get('next')
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect('/')
            else:
                # Invalid credentials entered
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


def account_register(request):
    """Register New User and send confirmation link to user's email id."""

    if request.method == 'POST':
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
                return HttpResponseRedirect('/accounts/register/')

            confirmation_code = ''.join(random.choice(
                string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
            profile = Profile(user=user, confirmation_code=confirmation_code)
            profile.save()
            send_registration_confirmation(user)

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


def confirm(request, confirmation_code, username):
    """Confirm User Account from the confirmation link sent to user's email id."""
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)

        if profile.confirmation_code == confirmation_code:
            user.is_active = True
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # Session Variable created to store if Moderator is using Forum
            # Becomes True only if moderator_home view (website.views) is accessed by user.
            request.session['MODERATOR_ACTIVATED'] = False

            messages.success(request, "Your account has been activated! Please update your profile to complete your registration.")
            return HttpResponseRedirect('/accounts/profile/')
        else:
            messages.error(request, "Something went wrong! Please try again!")
            return HttpResponseRedirect('/')

    except Exception:
        messages.error(request, "Your account not activated! Please try again!")
        return HttpResponseRedirect('/')


@login_required
def account_profile(request):
    """Complete Profile after Registration Confirmation."""
    user = request.user
    try:
        profile = Profile.objects.get(user_id=user.id)
    except:
        profile = Profile(user=user)

    if request.method == 'POST':
        form = ProfileForm(user, request.POST)
        if form.is_valid():
            # Save the user details
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            profile.address = request.POST['address']
            profile.phone = request.POST['phone']
            user.save()
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            profile.save()

            messages.success(request, "Your profile has been updated!")

            next = request.GET.get('next', '')
            try:
                resolve(next)
                return HttpResponseRedirect(next)
            except Resolver404:
                return HttpResponseRedirect("/accounts/view-profile/{0}/".format(user.id))

        # return account_view_profile(request, user.id)
        context = {'form':form}
        return render(request, 'forums/templates/profile.html', context)

    else:
        context = {}
        context.update(csrf(request))
        instance = profile
        context['form'] = ProfileForm(user, instance=instance)
        return render(request, 'forums/templates/profile.html', context)


@login_required
def account_view_profile(request, user_id=None):
    """Show user's details along with contribution made by user
       on the forum as Questions and Answers."""
    user = User.objects.get(pk=user_id)
    try:
        profile = Profile.objects.get(user=user)
    except:
        profile = Profile(user=user)

    flag = False   # True if user is requesting for his own profile
    if str(user_id) == str(request.user.id):
        flag = True

    if request.session.get('MODERATOR_ACTIVATED', False):
        # Moderators other than super moderator (forum_moderator)
        # should be able to view Ques/Ans of only their Categories.
        if request.user.groups.filter(name="forum_moderator").exists():
            questions = Question.objects.filter(user_id=user_id).order_by('-date_created')
            answers = Answer.objects.filter(uid=user_id).order_by('-date_created')
        else:
            questions = []
            answers = []
            for group in request.user.groups.all():
                category = ModeratorGroup.objects.get(group=group).category
                questions.extend(Question.objects.filter(
                    user_id=user_id, category__name=category.name))
                answers.extend(Answer.objects.filter(
                    uid=user_id, question__category__name=category.name))
            questions.sort(
                key=lambda question: question.date_created,
                reverse=True,
            )
            answers.sort(
                key=lambda answer: answer.date_created,
                reverse=True,
            )
    else:
        # Spammed questions should be visible if flag=True
        if flag:
            questions = Question.objects.filter(
                user_id=user_id, is_active=True).order_by('-date_created')
            answers = Answer.objects.filter(
                uid=user_id, is_active=True, question__is_active=True).order_by('-date_created')
        else:
            questions = Question.objects.filter(
                user_id=user_id, is_active=True, is_spam=False).order_by('-date_created')
            answers = Answer.objects.filter(
                uid=user_id, is_active=True,
                is_spam=False, question__is_active=True).order_by('-date_created')

    form = ProfileForm(user, instance=profile)

    context = {
        'show': flag,
        'profile' : profile,
        'questions' : questions,
        'answers' : answers,
        'form' : form,
    }
    return render(request, 'forums/templates/view-profile.html', context)


def user_logout(request):
    """Log out the User."""
    # No session variable for Anonymous Users
    if request.session.get('MODERATOR_ACTIVATED', None) is not None:
        del request.session['MODERATOR_ACTIVATED']

    logout(request)
    return HttpResponseRedirect('/')
