from django.utils.translation import ugettext_lazy as _

from django_vox import settings

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'twitter'
    PROTOCOL = 'twitter'
    ESCAPE_HTML = False
    VERBOSE_NAME = _('Twitter')
    DEPENDS = ('twitter',)

    @classmethod
    def send_message(cls, contact, message):
        import twitter
        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_TOKEN_KEY,
            access_token_secret=settings.TWITTER_TOKEN_SECRET,
        )
        if contact.address:
            api.PostDirectMessage(message, screen_name=contact.address)
        else:
            api.PostUpdate(message)
