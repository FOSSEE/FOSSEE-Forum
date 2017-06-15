from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from forums import views
from django.contrib.auth.views import password_reset, password_reset_confirm,\
    password_reset_done, password_reset_complete, password_change,\
    password_change_done

admin.autodiscover()

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'forums.views.home', name='home'),
    # url(r'^forums/', include('forums.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('website.urls', namespace='website')),
    url(r'^moderator/', include('moderator.urls', namespace='moderator')),
    url(r'^', include('django.contrib.auth.urls')),
    # for social authentication
    url(r'^oauth/', include('social_django.urls', namespace='social')),

    url(r'^forgotpassword/$',
        password_reset,
        {'template_name':
         'forums/templates/registration/password_reset_form.html'},
        name="password_reset"),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        {'template_name':
         'forums/templates/registration/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^password_reset/mail_sent/$',
        password_reset_done,
        {'template_name':
         'forums/templates/registration/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password_reset/complete/$',
        password_reset_complete,
        {'template_name':
         'forums/templates/registration/password_reset_complete.html'},
        name='password_reset_complete'),
    url(r'^changepassword/$',
        password_change,
        {'template_name':
         'forums/templates/registration/password_change_form.html'},
        name='password_change'),
    url(r'^password_change/done/$',
        password_change_done,
        {'template_name':
         'forums/templates/registration/password_change_done.html'},
        name='password_change_done'),

    # User account urls
    url(r'^accounts/login/', views.user_login, name='user_login'),
    url(r'^accounts/logout/', views.user_logout, name='user_logout'),
    url(r'^accounts/register/', views.account_register, name='user_register'),
    # url(r'^migrate', 'migrate_spoken.views.chenage_drupal_userid_spoken',
    # name='chenage_drupal_userid_spoken'),
    url(
     r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$",
     views.confirm, name='confirm'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$",
        views.account_profile,
        name='profile'),
    url(r"^accounts/view-profile/(?P<user_id>[\w. @-]+)/$",
        views.account_view_profile,
        name='view_profile'),
    # url(r'^ratings/', include('ratings.urls')),
    # url(r'^accounts/forgot-password/$', views.forgotpassword,
    # name='forgotpassword'),
    # url(r'^accounts/update-password/$', views.updatepassword,
    # name='updatepassword'),
)
