from django.utils.translation import ugettext_lazy as _

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

    @classmethod
    def send_message(cls, _from_address, to_addresses, message):
        import twitter
        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_TOKEN_KEY,
            access_token_secret=settings.TWITTER_TOKEN_SECRET,
        )
        if not to_addresses:
            api.PostUpdate(message)
        else:
            for address in to_addresses:
                api.PostDirectMessage(message, screen_name=address)
