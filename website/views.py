import math

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404

from website.models import Post, Reply, TutorialDetails, TutorialResources
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
    context = {
        'categories': categories
    }
    return render_to_response('website/templates/index.html', context)

def fetch_tutorials(request, category=None):
    tutorials = TutorialDetails.objects.using('spoken').filter(foss_category=category)
    context = {
        'category': category,
        'tutorials': tutorials
    }
    return render_to_response('website/templates/fetch_tutorials.html', context)

def fetch_posts(request, category=None, tutorial=None):
    posts = Post.objects.filter(category=category).filter(tutorial=tutorial)
    context = {
        'category': category,
        'tutorial': tutorial,
        'posts': posts
    }
    return render_to_response('website/templates/fetch_posts.html', context)


def get_post(request, post_id=None):
    post = get_object_or_404(Post, id=post_id)
    replies = post.reply_set.all()
    context = {
        'post': post,
        'replies': replies
    }
    return render_to_response('website/templates/get_post.html', context)

def new_post(request):
    video_info = get_video_info('/home/cheese/test-video.ogv')
    duration = math.ceil(video_info['duration']/60) #assuming the video is less than an hour
    return HttpResponse(duration)






















