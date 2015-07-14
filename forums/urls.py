from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'forums.views.home', name='home'),
    # url(r'^forums/', include('forums.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('website.urls', namespace='website')),
    # User account urls
    url(r'^accounts/login/', 'forums.views.user_login', name='user_login'),
    url(r'^accounts/logout/', 'forums.views.user_logout', name='user_logout'),
    url(r'^accounts/register/', 'forums.views.account_register', name='user_register'),
    url(r'^migrate', 'migrate_spoken.views.chenage_drupal_userid_spoken', name='chenage_drupal_userid_spoken'),
    url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", 'forums.views.confirm', name='confirm'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", 'forums.views.account_profile', name='profile'),
    url(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$", 'forums.views.account_view_profile', name='view_profile'),
   
    
)
