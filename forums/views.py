from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response , render, redirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.urlresolvers import reverse
import urllib
import urllib2
import json
import random, string
from forums.forms import *
from website.models import *

# to register new user and send confirmation link to registerd email id
def account_register(request):
    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print ("ok")
        
        if form.is_valid():

            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            result = json.load(response)
            ''' End reCAPTCHA validation '''
            print result['success']
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']
            user = User.objects.create_user(username, email, password)
            user.is_active = False
            print result['success']
            if result['success']:
                user.save()
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')

            confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
            p = Profile(user=user, confirmation_code=confirmation_code)
            p.save()
            send_registration_confirmation(user)
            messages.success(request, """
                Please confirm your registration by clicking on the activation link which has been sent to your registered email id.
            """)
            return render(request, 'forums/templates/message.html')
        context = {'form':form,
                    'SITE_KEY': settings.GOOGLE_RECAPTCHA_SITE_KEY }
        return render_to_response('forums/templates/user-register.html', context,context_instance = RequestContext(request))
    else:
        form = RegisterForm()
        context = {
            'form': form,
            'SITE_KEY': settings.GOOGLE_RECAPTCHA_SITE_KEY
        }
        context.update(csrf(request))
        return render_to_response('forums/templates/user-register.html', context)

# alert user after user account confirmation
def confirm(request, confirmation_code, username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        #if profile.confirmation_code == confirmation_code and user.date_joined > (timezone.now()-timezone.timedelta(days=1)):
        if profile.confirmation_code == confirmation_code:
            user.is_active = True
            user.save()
            user.backend='django.contrib.auth.backends.ModelBackend' 
            login(request,user)
           
            messages.success(request, "Your account has been activated!. Please update your profile to complete your registration")
            return HttpResponseRedirect('/accounts/profile/'+user.username)
        else:
            
            messages.success(request, "Something went wrong!. Please try again!")
            return HttpResponseRedirect('/')
    except Exception, e:
        messages.success(request, "Your account not activated!. Please try again!")
        return HttpResponseRedirect('/')


# add details to the profile table of the user
# update profile after registration confirmation
@login_required
def account_profile(request, username):
    user = request.user
    profile = Profile.objects.get(user_id=user.id)
    #old_file_path = settings.MEDIA_ROOT + str(profile.picture)
    #new_file_path = None
    if request.method == 'POST':
        form = ProfileForm(user, request.POST)
        if form.is_valid():
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            profile.address = request.POST['address']
            profile.phone = request.POST['phone']
            user.save()
            form_data = form.save(commit=False)
            form_data.user_id = user.id
            
            # if 'picture-clear' in request.POST and request.POST['picture-clear']:
            #     #if not old_file == new_file:
            #     if os.path.isfile(old_file_path):
            #         os.remove(old_file_path)
            #
            # if 'picture' in request.FILES:
            #     form_data.picture = request.FILES['picture']
            
            #form_data.save()
            #profile.address = address
            #profile.phone = phone
            profile.save()
            
            """if 'picture' in request.FILES:
                size = 128, 128
                filename = str(request.FILES['picture'])
                ext = os.path.splitext(filename)[1]
                if ext != '.pdf' and ext != '':
                    im = Image.open(settings.MEDIA_ROOT + str(form_data.picture))
                    im.thumbnail(size, Image.ANTIALIAS)
                    ext = ext[1:]
                    
                    mimeType = ext.upper()
                    if mimeType == 'JPG':
                        mimeType = 'JPEG'
                    im.save(settings.MEDIA_ROOT + "user/" + str(user.id) + "/" + str(user.id) + "-thumb." + ext, mimeType)
                    form_data.thumb = 'user/' + str(user.id)+ '/' + str(user.id) + '-thumb.' + ext
                    form_data.save()"""
            messages.success(request, "Your profile has been updated!")
            return HttpResponseRedirect("/accounts/view-profile/{0}".format(user.id))
        # return account_view_profile(request, user.id)

        context = {'form':form}
        return render(request, 'forums/templates/profile.html', context)
    else:
        context = {}
        context.update(csrf(request))
        instance = Profile.objects.get(user_id=user.id)
        context['form'] = ProfileForm(user, instance = instance)
        return render(request, 'forums/templates/profile.html', context) 
        
# view all profile details saved for the user, when clicked on my profile  
@login_required
def account_view_profile(request, user_id):
    
    user = User.objects.get(pk = user_id)
    profile = Profile.objects.get(user=user)
    flag = False
    
    marker = 0
    if 'marker' in request.GET:
        marker = int(request.GET['marker'])

    total = Question.objects.filter(user_id=user_id).count()
    total = int(total - (total % 10 - 10))
    questions = Question.objects.filter(user_id=user_id).order_by('date_created').reverse()[marker:marker+10]
    total1 = Answer.objects.filter(uid=user_id).count()
    total1 = int(total1 - (total1 % 10 - 10))
    answers = Answer.objects.filter(uid=user_id).order_by('date_created').reverse()[marker:marker+10]
    form = ProfileForm(user, instance = profile)

    if str(user_id) == str(request.user.id):
        flag = True

    context = {
        'show': flag,
        'profile' : profile,
        'media_url' : settings.MEDIA_URL,
        'questions' : questions,
        'answers' : answers,
        'form' : form,
        'user_show':user,   
    }
    return render(request, 'forums/templates/view-profile.html', context)
    
    
                
# send confirm registration link    
def send_registration_confirmation(user):
    p = Profile.objects.get(user=user)
     
    # Sending email when an answer is posted
    subject = 'Account Active Notification'
    message = """Dear {0},\n
    Thank you for registering at {1}.\n\n You may activate your account by clicking on this link or copying and pasting it in your browser
    {2}\n
    Regards,\n
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
        headers={'Reply-To': settings.SENDER_EMAIL, "Content-type":"text/html;charset=iso-8859-1"}
    )
    email.attach_alternative(message, "text/html")
    try:
        result = email.send(fail_silently=False)
    except:
        pass

# user login        
def user_login(request):

    if request.user.is_anonymous():

        if request.method == 'POST':
            form = UserLoginForm(request.POST)

            # Valid credentials are entered
            if form.is_valid():
                
                cleaned_data = form.cleaned_data
                user = cleaned_data.get("user")
                login(request, user)

                if 'next' in request.POST:
                    next_url = request.POST.get('next')
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect('/')
            
            # Invalid credentials entered
            else:
                next_url = request.POST.get('next')
                context = {
                    'form': form,
                    'next': next_url,
                    #'password_reset': True if next_url else False
                }
                context.update(csrf(request))
                return render_to_response('forums/templates/user-login.html', context)
                
        else:
            form = UserLoginForm()
        
        next_url = request.GET.get('next')
        context = {
            'form': form,
            'next': next_url,
            #'password_reset': True if next_url else False
        }
        context.update(csrf(request))
        return render_to_response('forums/templates/user-login.html', context)

    else:
        return HttpResponseRedirect('/')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

# def forgotpassword(request):
#     context = {}
#     user_emails = []
#     context.update(csrf(request))
#     if request.method == 'POST':
#         users = User.objects.all()
#         for user in users:
#             user_emails.append(user.email)
#         email = request.POST['email']
#         if email == "":
#             context['invalid_email'] = True
#             return render_to_response("forums/templates/forgot-password.html", context)
#         if email in user_emails:
#             user = User.objects.get(email=email)
#             password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
#             user.set_password(password)
#             user.save()
#             sender_name = "FOSSEE Forums"
#             sender_email = settings.SENDER_EMAIL
#             subject = "FOSSEE Forums - Password Reset"
#             to = (user.email, )
#       url = settings.EMAIL_URL
#             message = """Dear """+user.username+""",\nYour password for FOSSEE Forums has been reset. Your credentials are:\nUsername: """+user.username+"""\nPassword: """+password+"""\n\nWe recommend you to login with the given credentials & update your password immediately.\nLink to set new password: """+url+"""/accounts/login/?next=/accounts/update-password/\nThank You !\nRegards,\nFOSSEE Team,\n IIT Bombay."""
#       send_mail(subject, message, sender_email, to)
#             form = UserLoginForm()
#             context['form'] = form
#             #context['password_reset'] = True
#             return HttpResponseRedirect('/accounts/login/?next=/accounts/update-password/')
#             #return render_to_response("forums/templates/user-login.html", context)
#         else:
#             context['invalid_email'] = True
#             return render_to_response("forums/templates/forgot-password.html", context)
#     else:
#         return render_to_response('forums/templates/forgot-password.html', context)

# def updatepassword(request):
#     context = {}
#     user = request.user
#     context.update(csrf(request))
#     if user.is_authenticated():
#         if request.method == 'POST':
#             new_password = request.POST['new_password']
#             confirm = request.POST['confirm_new_password']
#             if new_password == "" or confirm == "":
#                 context['empty'] = True
#                 return render_to_response("update-password.html", context)
#             if new_password == confirm:
#                 user.set_password(new_password)
#                 user.save()
#                 context['password_updated'] = True
#                 logout(request)
#                 form = UserLoginForm()
#                 context['form'] = form
#                 #return render_to_response('website/templates/index.html', context)
#       return HttpResponseRedirect('/')
#             else:
#                 context['no_match'] = True
#                 return render_to_response("forums/templates/update-password.html", context)
#         else:
#             return render_to_response("forums/templates/update-password.html", context)
#     else:
#         form = UserLoginForm()
#         context['form'] = form
#         context['for_update_password'] = True
#         return render_to_response('website/templates/index.html', context)
