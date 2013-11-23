from django import template

from website.models import Post, Reply

register = template.Library()

def category_post_count(category):
    category_post_count = Post.objects.filter(category=category).count()
    return category_post_count
register.simple_tag(category_post_count)

