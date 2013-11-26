from django.conf.urls import patterns, include, url
from referendum import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.example, name='example'),
    url(r'^vote/$', views.vote, name='vote'),
)
