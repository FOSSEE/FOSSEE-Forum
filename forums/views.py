from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from forums.forms import UserLoginForm

def user_login(request):
    if request.user.is_anonymous():
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.POST:
                        next_url = request.POST.get('next')
                        return HttpResponseRedirect(next_url)
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponse('you are blocked')
            else:
                return HttpResponse('Invalid username or password')
        else:
            form = UserLoginForm()
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
