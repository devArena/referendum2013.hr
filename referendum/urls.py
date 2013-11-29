from django.conf.urls import patterns, include, url
from referendum import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.example, name='example'),
    url(r'^vote/$', views.vote, name='vote'),
    url(r'^croatia/$', views.local_map, name='local_map'),
    url(r'^world/$', views.world_map, name='world_map'),
    url(r'^data/(?P<scope>country|county)/(?P<location>current|hometown)/$',
        views.fetch_country_data,
        name='data:scope:location'
    ),
    url(r'^age/$', views.age_hchart, name='age_hchart'),
    url(r'^data/age/$', views.fetch_global_ageresults, name='data:age'),
)
