from django.utils.translation import ugettext_lazy as _
import django.conf

from django_vox import settings

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'twitter'
    PROTOCOL = 'twitter'
    EDITOR_TYPE = 'basic'
    ESCAPE_HTML = False
    VERBOSE_NAME = _('Twitter')
    DEPENDS = ('twitter',)

    def __init__(self):
        kwargs = {
            'consumer_key': settings.TWITTER_CONSUMER_KEY,
            'consumer_secret': settings.TWITTER_CONSUMER_SECRET,
            'access_token_key': settings.TWITTER_TOKEN_KEY,
            'access_token_secret': settings.TWITTER_TOKEN_SECRET,
        }
        if None in kwargs.values():
            raise django.conf.ImproperlyConfigured(
                'Twitter backend enabled but settings are missing')

        import twitter
        self.client = twitter.Api(**kwargs)

    def send_message(self, _from_address, to_addresses, message):
        if not to_addresses:
            self.client.PostUpdate(message)
        else:
            for address in to_addresses:
                self.client.PostDirectMessage(message, screen_name=address)
