"""
Django settings for api documentation generation
"""

from tests.settings import *  # noqa: F403,F401

INSTALLED_APPS = BASE_INSTALLED_APPS + [
    'tests', 'background_task']

