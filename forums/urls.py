from django.urls import include, path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from forums import views
from django.contrib.auth.views import password_reset, password_reset_confirm, \
        password_reset_done, password_reset_complete, password_change, \
        password_change_done

admin.autodiscover()

urlpatterns = [

    # Examples:
    # path(r'^$', 'forums.views.home', name = 'home'),
    # path(r'^forums/', include('forums.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
    path('', include('website.urls')),

    # URLs for password reset and password change
    path('forgotpassword/', password_reset, {'template_name': 'forums/templates/registration/password_reset_form.html'}, name = "password_reset"),
    url(r'^password_reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm, {'template_name': 'forums/templates/registration/password_reset_confirm.html'}, name = 'password_reset_confirm'),
    path('password_reset/mail_sent/', password_reset_done, {'template_name': 'forums/templates/registration/password_reset_done.html'},
        name = 'password_reset_done'),
    path('password_reset/complete/', password_reset_complete, {'template_name': 'forums/templates/registration/password_reset_complete.html'},
        name = 'password_reset_complete'),
    path('changepassword/', password_change, {'template_name': 'forums/templates/registration/password_change_form.html', \
        'post_change_redirect':'password_change_done'}, name = 'password_change'),
    path('password_change/done/', password_change_done, {'template_name': 'forums/templates/registration/password_change_done.html'},
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

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
