from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

from forums.forms import UserLoginForm

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
