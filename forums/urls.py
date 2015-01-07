from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'forums.views.home', name='home'),
    # url(r'^forums/', include('forums.foo.urls')),
    url(r'^', include('website.urls', namespace='website')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    # User account urls
    url(r'^accounts/login/', 'forums.views.user_login', name='user_login'),
    url(r'^accounts/logout/', 'forums.views.user_logout', name='user_logout'),
    url(r'^migrate', 'migrate_spoken.views.chenage_drupal_userid_spoken', name='chenage_drupal_userid_spoken'),
)
