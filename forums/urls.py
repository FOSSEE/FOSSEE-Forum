from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, password_reset_complete, password_change, password_change_done
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
    url(r'^', include('django.contrib.auth.urls')),

    url(r'^forgotpassword/$', password_reset, {'template_name': 'forums/templates/password_reset.html'}, name='password_reset'),
    url(r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',password_reset_confirm, {'template_name': 'forums/templates/password_Reset_confirm.html'}, name='password_reset_confirm'), #{'template_name': 'forums/templates/password_reset_confirm.html'}
    url(r'^password_reset/mail_sent/$', password_reset_done, {'template_name': 'forums/templates/password_reset_mail.html'}, name='password_reset_done'), #{'template_name': 'forums/templates/password_reset_mail.html'}
    url(r'^password_reset/complete/$', password_reset_complete, {'template_name': 'forums/templates/password_reset_complete.html'}, name='password_reset_complete'), #, {'template_name': 'forums/templates/password_reset_complete.html'}
    url(r'^password_change/done/$', password_change_done, {'template_name': 'forums/templates/password_reset_done.html'},name='password_change_done'),
    
    # User account urls
    url(r'^accounts/login/', 'forums.views.user_login', name='user_login'),
    url(r'^accounts/logout/', 'forums.views.user_logout', name='user_logout'),
    url(r'^accounts/register/', 'forums.views.account_register', name='user_register'),
    url(r'^migrate', 'migrate_spoken.views.chenage_drupal_userid_spoken', name='chenage_drupal_userid_spoken'),
    url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", 'forums.views.confirm', name='confirm'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", 'forums.views.account_profile', name='profile'),
    url(r"^accounts/view-profile/(?P<user_id>[\w. @-]+)/$", 'forums.views.account_view_profile', name='view_profile'),
    url(r'^accounts/forgot-password/$', 'forums.views.forgotpassword', name='forgotpassword'),
    url(r'^accounts/update-password/$', 'forums.views.updatepassword', name='updatepassword'), 
   
    
)
