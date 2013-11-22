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
    url(r'^example/$', views.example, name='example'),
    url(r'^(?P<facebook_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^results/$', views.results, name='results'),
    url(r'^friends_results/$', views.friends_results, name='results'),
)
