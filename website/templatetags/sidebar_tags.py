from django import template

from website.models import Post, Reply

register = template.Library()

def recent_posts():
    recent_posts = Post.objects.all().order_by('-id')[:5]
    return {'recent_posts': recent_posts}

register.inclusion_tag('website/templates/recent_posts.html')(recent_posts)

