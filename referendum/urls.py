from django.conf.urls import patterns, include, url
from referendum import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^project/', include('project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.example, name='example'),
    #url(r'^stressTest/$', views.stressTest, name='stressTest'),
    #url(r'^friendsStressTest/$', views.friendsStressTest, name='friendsStressTest'),
    #url(r'^exampleStressTest/$', views.exampleStressTest, name='exampleStressTest'),
    url(r'^vote/$', views.vote, name='vote'),
    url(r'^results/$', views.results, name='results'),
    url(r'^friends_results/$', views.friends_results, name='friends_results'),
)
