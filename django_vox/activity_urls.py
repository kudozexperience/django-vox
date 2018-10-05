"""
URL patterns for testing app.

We don't have any for now.
"""
from django.conf.urls import include, url

from . import views

sub_patterns = [
    url(r'^following$', views.empty),
    url(r'^followers$', views.empty),
    url(r'^liked$', views.empty),
    url(r'^inbox$', views.inbox),
    url(r'^outbox$', views.empty),
    url(r'^$', views.endpoint),
]
urlpatterns = [
    url(r'^(?P<path>.*)/', include(sub_patterns)),
]
