import importlib.util
import pydoc
import re
import sys

import django.conf

__all__ = ('BACKENDS', 'MARKDOWN_EXTRAS', 'MARKDOWN_LINK_PATTERNS',
           'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER',
           'TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET',
           'TWITTER_TOKEN_KEY', 'TWITTER_TOKEN_SECRET',
           'XMPP_JID', 'XMPP_PASSWORD', 'POSTMARK_TOKEN')


# General settings
BACKENDS = []

# Markdown settings
URL_PATTERN = re.compile(
    r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]'
    r'+(:[0-9]+)?|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+'
    r'~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
MARKDOWN_EXTRAS = ['footnotes', 'link_patterns', 'smarty-pants', 'tables']
MARKDOWN_LINK_PATTERNS = [(URL_PATTERN, r'\1')]

# Twilio
TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None
TWILIO_FROM_NUMBER = None

# Twitter settings
TWITTER_CONSUMER_KEY = None
TWITTER_CONSUMER_SECRET = None
TWITTER_TOKEN_KEY = None
TWITTER_TOKEN_SECRET = None

# XMPP settings
XMPP_JID = None
XMPP_PASSWORD = None

# Postmark
POSTMARK_TOKEN = None


class _Sneaky:
    def __init__(self, name):
        self.module = sys.modules[name]
        sys.modules[name] = self
        # sphinx would like me to do something like this, but it
        # breaks things right now
        # for name in __all__:
        #     if name != 'BACKENDS':
        #         setattr(self, name, getattr(self.module, name))

    def __getattr__(self, name):
        # call module.__init__ after import introspection is done
        django_setting_name = 'DJANGO_VOX_' + name
        if name in __all__:
            if hasattr(django.conf.settings, django_setting_name):
                return getattr(django.conf.settings, django_setting_name)
            elif name == 'BACKENDS':
                return super().__getattr__(name)
        result = getattr(self.module, name)
        if result is None:
            raise django.conf.ImproperlyConfigured(
                'Please set {} in your settings'.format(django_setting_name))
        return result

    def get_backends(self):
        result = []
        # Automatically set based on libraries available
        default_backends = [
            'django_vox.backends.html_email.Backend',
            'django_vox.backends.markdown_email.Backend',
            'django_vox.backends.postmark_email.Backend',
            'django_vox.backends.template_email.Backend',
            'django_vox.backends.twilio.Backend',
            'django_vox.backends.twitter.Backend',
            'django_vox.backends.slack.Backend',
            'django_vox.backends.json_webhook.Backend',
            'django_vox.backends.xmpp.Backend',
        ]
        for cls_str in default_backends:
            cls = pydoc.locate(cls_str)
            for dep in cls.DEPENDS:
                if importlib.util.find_spec(dep) is None:
                    continue
            result.append(cls_str)
        return result

    BACKENDS = property(get_backends, doc="hello world")


_Sneaky(__name__)
