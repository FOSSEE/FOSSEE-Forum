from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response , render
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
from website.models import *

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
            p = Profile(user=user, confirmation_code=confirmation_code)
            p.save()
            send_registration_confirmation(user)
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
            print "In if"
            messages.success(request, "Your account has been activated!. Please update your profile to complete your registration")
            return HttpResponseRedirect('/accounts/profile/'+user.username)
        else:
            print "In else"
            messages.success(request, "Something went wrong!. Please try again!")
            return HttpResponseRedirect('/')
    except Exception, e:
        print "In excepw"
        messages.success(request, "Your account not activated!. Please try again!")
        return HttpResponseRedirect('/')
        
@login_required
def account_logout(request):
    context = RequestContext(request)
    logout(request)
    return HttpResponseRedirect('/')

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
            
            form_data.save()
            
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
            return HttpResponseRedirect("/accounts/view-profile/" + user.username)
        
        context = {'form':form}
        return render(request, 'forums/templates/profile.html', context)
    else:
        context = {}
        context.update(csrf(request))
        instance = Profile.objects.get(user_id=user.id)
        context['form'] = ProfileForm(user, instance = instance)
        return render(request, 'forums/templates/profile.html', context)
  
@login_required
def account_view_profile(request, username):
    
    user = User.objects.get(username = username)
    profile = Profile.objects.filter(user = user)[0]
    context = {
        'profile' : profile,
        'media_url' : settings.MEDIA_URL,
    }
    return render(request, 'forums/templates/view-profile.html', context)
                

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
		"http://fossee.in",
		"http://localhost:8000/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
	)
	email = EmailMultiAlternatives(
		subject, message, 'sysads@fossee.in',
		to = [user.email], bcc = [], cc = [],
		headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
	)
	print message
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
