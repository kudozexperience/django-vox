import importlib.util
import pydoc
import re

import django.conf

URL_PATTERN = re.compile(
    r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]'
    r'+(:[0-9]+)?|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+'
    r'~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')

BACKENDS = getattr(django.conf.settings, 'DJANGO_VOX_BACKENDS', None)
if BACKENDS is None:
    BACKENDS = []
    # Automatically set based on libraries available
    default_backends = [
        'django_vox.backends.html_email.Backend',
        'django_vox.backends.markdown_email.Backend',
        'django_vox.backends.postmark_email.Backend',
        'django_vox.backends.template_email.Backend',
        'django_vox.backends.twilio.Backend',
        'django_vox.backends.slack.Backend',
        'django_vox.backends.json_webhook.Backend',
    ]
    for cls_str in default_backends:
        cls = pydoc.locate(cls_str)
        for dep in cls.DEPENDS:
            if importlib.util.find_spec(dep) is None:
                continue
        BACKENDS.append(cls_str)

MARKDOWN_EXTRAS = getattr(django.conf.settings,
                          'DJANGO_VOX_MARKDOWN_EXTRAS', None)
if MARKDOWN_EXTRAS is None:
    MARKDOWN_EXTRAS = ['footnotes', 'link_patterns', 'smarty-pants', 'tables']

MARKDOWN_LINK_PATTERNS = getattr(django.conf.settings,
                                 'DJANGO_VOX_MARKDOWN_LINK_PATTERNS', None)
if MARKDOWN_LINK_PATTERNS is None:
    MARKDOWN_LINK_PATTERNS = [(URL_PATTERN, r'\1')]

SENDER_MODEL = getattr(django.conf.settings,
                       'DJANGO_VOX_SENDER_MODEL', None)
RECIPIENT_MODEL = getattr(django.conf.settings,
                          'DJANGO_VOX_RECIPIENT_MODEL', None)
