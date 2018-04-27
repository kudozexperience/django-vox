import re

import django.conf

URL_PATTERN = re.compile(
    r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]'
    r'+(:[0-9]+)?|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+'
    r'~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')

BACKENDS = getattr(django.conf.settings, 'DJANGO_VOX_BACKENDS', None)
if BACKENDS is None:
    # Automatically set based on libraries available
    BACKENDS = ['django_vox.backends.EmailBackend',
                'django_vox.backends.SlackWebhookBackend']
    try:
        import august  # noqa: F401
        BACKENDS.append('django_vox.backends.HtmlEmailBackend')
    except ImportError:
        pass
    try:
        import markdown2  # noqa: F401
        BACKENDS.append('django_vox.backends.MarkdownEmailBackend')
    except ImportError:
        pass
    try:
        import twilio.rest  # noqa: F401
        BACKENDS.append('django_vox.backends.TwilioBackend')
    except ImportError:
        pass
    try:
        import lxml  # noqa: F401
        BACKENDS.append('django_vox.backends.PostmarkTemplateBackend')
    except ImportError:
        pass

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
