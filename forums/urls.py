from django.urls import include, path, re_path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from forums import views
from django.contrib.auth import views as auth_views

admin.autodiscover()
urlpatterns = [

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('website.urls', namespace='website')),

    # URLs for password reset and password change
    re_path('^forgotpassword/', auth_views.PasswordResetView.as_view(\
    template_name= 'forums/templates/registration/password_reset_form.html'),\
    name = "password_reset"),

    re_path(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',\
    auth_views.PasswordResetConfirmView.as_view(\
    template_name= 'forums/templates/registration/password_reset_confirm.html'\
    ), name = 'password_reset_confirm'),

    re_path(r'^password_reset/mail_sent/', \
    auth_views.PasswordResetDoneView.as_view(template_name= \
    'forums/templates/registration/password_reset_done.html'),\
    name = 'password_reset_done'),

    re_path(r'^password_reset/complete/', auth_views.\
    PasswordResetCompleteView.as_view(template_name= \
    'forums/templates/registration/password_reset_complete.html'),\
    name = 'password_reset_complete'),

    re_path(r'^changepassword/', auth_views.PasswordChangeView.as_view(\
    template_name='forums/templates/registration/password_change_form.html'), name = 'password_change'),

    re_path(r'^password_change/done/', auth_views.\
    PasswordChangeDoneView.as_view(template_name= \
    'forums/templates/registration/password_change_done.html'),\
    name = 'password_change_done'),

    # User account URLs
    path('accounts/login/', views.user_login, name = 'user_login'),
    path('accounts/logout/', views.user_logout, name = 'user_logout'),
    path('accounts/register/', views.account_register, name = 'user_register'),
    path('accounts/confirm/<str:confirmation_code>/<str:username>/', views.confirm, name = 'confirm'),
    path('accounts/profile/', views.account_profile, name = 'profile'),
    path('accounts/view-profile/<int:user_id>/', views.account_view_profile, name = 'view_profile'),

    path('ckeditor/', include('ckeditor_uploader.urls')),

]

#urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
