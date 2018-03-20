"""
URL patterns for testing app.

We don't have any fore now.
"""
from django.conf.urls import url

from . import views

app_name = 'tests'
urlpatterns = [
    url(r'^$', views.article_list, name='index'),
    url(r'^(?P<article_id>[0-9]+)/$', views.article_detail, name='detail'),
    url(r'^subscribe$', views.subscribe, name='subscribe'),
    url(r'^(?P<article_id>[0-9]+)/comment$', views.comment, name='comment'),
]
