from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from forums import views
from django.contrib.auth.views import password_reset, password_reset_confirm,\
        password_reset_done, password_reset_complete, password_change,\
        password_change_done

admin.autodiscover()

urlpatterns = [
    url(r'^forgotpassword/$', password_reset, name="password_reset"),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^password_reset/mail_sent/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password_reset/complete/$', password_reset_complete,
        name='password_reset_complete'),
    url(r'^changepassword/$', password_change,
        name='password_change'),
    url(r'^password_change/done/$', password_change_done,
        name='password_change_done'),
    url(r'^tinymce/', include('tinymce.urls')),
]

urlpatterns += [
    # Examples:
    # url(r'^$', 'forums.views.home', name='home'),
    # url(r'^forums/', include('forums.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('website.urls', namespace='website')),
    # User account urls
    url(r'^accounts/login/', views.user_login, name='user_login'),
    url(r'^accounts/logout/', views.user_logout, name='user_logout'),
    url(r'^accounts/register/', views.account_register, name='user_register'),
    #url(r'^migrate', chenage_drupal_userid_spoken, name='chenage_drupal_userid_spoken'),
    url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", views.confirm, name='confirm'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", views.account_profile, name='profile'),
    url(r"^accounts/view-profile/(?P<user_id>[\w. @-]+)/$", views.account_view_profile, name='view_profile'),
    ]