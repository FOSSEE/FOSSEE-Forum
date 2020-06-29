from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from forums import views
from django.contrib.auth import views as auth_views

admin.autodiscover()

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('website.urls', namespace='website')),

    # User account URLs
    path('accounts/login/', views.user_login, name = 'user_login'),
    path('accounts/logout/', views.user_logout, name = 'user_logout'),
    path('accounts/register/', views.account_register, name = 'user_register'),
    path('accounts/confirm/<str:confirmation_code>/<str:username>/', views.confirm, name = 'confirm'),
    path('accounts/profile/', views.account_profile, name = 'profile'),
    path('accounts/view-profile/<int:user_id>/', views.account_view_profile, name = 'view_profile'),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    # Django Auth URLs
    path('forgotpassword/',
         auth_views.PasswordResetView.as_view(
            template_name='forums/templates/registration/password_reset_form.html',
            email_template_name ='forums/templates/registration/password_reset_email.html',
            subject_template_name ='forums/templates/registration/password_reset_subject.txt',
            from_email=settings.SENDER_EMAIL),
         name="password_reset",
    ),

    path('password_reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
            template_name='forums/templates/registration/password_reset_confirm.html'), 
         name='password_reset_confirm',
    ),

    path('password_reset/mail_sent/',
         auth_views.PasswordResetDoneView.as_view(
            template_name='forums/templates/registration/password_reset_done.html'),
         name='password_reset_done',
    ),

    path('password_reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
            template_name='forums/templates/registration/password_reset_complete.html'),
         name='password_reset_complete',
    ),

    path('changepassword/',
         auth_views.PasswordChangeView.as_view(
            template_name='forums/templates/registration/password_change_form.html'),
         name='password_change',
    ),

    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
            template_name='forums/templates/registration/password_change_done.html'),
         name='password_change_done',
    ),

]

#urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
