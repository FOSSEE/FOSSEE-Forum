from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.utils import timezone


from django.conf import settings



import random, string

from forums.forms import *

def account_register(request):
    context = {}
    print "account_registration"
    print request.method
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print form
        print form.is_valid
        if form.is_valid():
        
            username = request.POST['username']
            print username 
            password = request.POST['password']
            print password
            email = request.POST['email']
            print email
            user = User.objects.create_user(username, email, password)
            user.is_active = True
            user.save()
            confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
            #p = Profile(user=user, confirmation_code=confirmation_code)
            #p.save()
            #send_registration_confirmation(user)
            messages.success(request, """
                Please confirm your registration by clicking on the activation link which has been sent to your registered email id.
            """)
            return HttpResponseRedirect('/')
        context = {'form':form}
        return render_to_response('forums/templates/user-register.html', context,context_instance = RequestContext(request))
    else:
        form = RegisterForm()
        context = {
            'form': form
        }
        context.update(csrf(request))
        return render_to_response('forums/templates/user-register.html', context)

def send_registration_confirmation(user):
	p = Profile.objects.get(user=user)
	user.email = "ashwinids03@gmail.com"
	# Sending email when an answer is posted
	subject = 'Account Active Notification'
	message = """Dear {0},
	Thank you for registering at {1}. You may activate your account by clicking on this link or copying and pasting it in your browser
	{2}
	Regards,
	Admin
	FOSSEE forum
	IIT Bombay.
	""".format(
		user.username,
		"http://spoken-tutorial.org",
		"http://spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
	)
	email = EmailMultiAlternatives(
		subject, message, 'sysads@fossee.in',
		to = [user.email], bcc = [], cc = [],
		headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
	)
	email.attach_alternative(message, "text/html")
	try:
		result = email.send(fail_silently=False)
	except:
		pass
		
def user_login(request):
    if request.user.is_anonymous():
    	
        if request.method == 'POST':
            form = UserLoginForm(request.POST)
           
            if form.is_valid():
            	
                cleaned_data = form.cleaned_data
                
                user = cleaned_data.get("user")
                
                login(request, user)
                if 'next' in request.POST:
                    next_url = request.POST.get('next')
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect('/')
        else:
            form = UserLoginForm()
            print form.errors
        
        next_url = request.GET.get('next')
        context = {
            'form': form,
            'next': next_url
        }
        
        context.update(csrf(request))
        return render_to_response('forums/templates/user-login.html', context)
    else:
        return HttpResponseRedirect('/')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
