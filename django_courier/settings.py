import re

import django.conf
from django.utils.translation import ugettext_lazy as _

URL_PATTERN = re.compile(
    r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]'
    r'+(:[0-9]+)?|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+'
    r'~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')

BACKENDS = getattr(django.conf.settings, 'DJANGO_COURIER_BACKENDS', None)
if BACKENDS is None:
    # Automatically set based on libraries available
    BACKENDS = ['django_courier.backends.EmailBackend',
                'django_courier.backends.SlackWebhookBackend']
    try:
        import markdown2  # noqa: F401
        BACKENDS.append('django_courier.backends.MarkdownEmailBackend')
    except ImportError:
        pass
    try:
        import twilio.rest  # noqa: F401
        BACKENDS.append('django_courier.backends.TwilioBackend')
    except ImportError:
        pass

CHANNELS = getattr(django.conf.settings, 'DJANGO_COURIER_CHANNELS', None)
if CHANNELS is None:
    CHANNELS = {
        '': (_('Sender'), _('Recipient')),
    }

MARKDOWN_EXTRAS = getattr(django.conf.settings,
                          'DJANGO_COURIER_MARKDOWN_EXTRAS', None)
if MARKDOWN_EXTRAS is None:
    MARKDOWN_EXTRAS = ['footnotes', 'link_patterns', 'smarty-pants', 'tables']

MARKDOWN_LINK_PATTERNS = getattr(django.conf.settings,
                                 'DJANGO_COURIER_MARKDOWN_LINK_PATTERNS', None)
if MARKDOWN_LINK_PATTERNS is None:
    MARKDOWN_LINK_PATTERNS = [(URL_PATTERN, r'\1')]

SENDER_MODEL = getattr(django.conf.settings,
                       'DJANGO_COURIER_SENDER_MODEL', None)
RECIPIENT_MODEL = getattr(django.conf.settings,
                          'DJANGO_COURIER_RECIPIENT_MODEL', None)
