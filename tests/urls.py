"""
URL patterns for testing app.

We don't have any fore now.
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles import views

urlpatterns = [
    url('^admin/', admin.site.urls),
] + [
    url(r'^static/(?P<path>.*)$', views.serve),
]

