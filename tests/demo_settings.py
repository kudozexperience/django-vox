"""
Django settings for django_courier demo
"""

from tests.settings import *  # noqa: F403,F401

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django_courier',
    'tests.apps.CourierDemoConfig',
]
