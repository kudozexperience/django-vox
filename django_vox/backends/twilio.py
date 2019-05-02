import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.utils.translation import ugettext_lazy as _

from django_vox import settings

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'twilio'
    PROTOCOL = 'sms'
    USE_FROM_ADDRESS = True
    ESCAPE_HTML = False
    EDITOR_TYPE = 'basic'
    VERBOSE_NAME = _('Twilio')
    DEPENDS = ('twilio',)

    def __init__(self):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        if account_sid is None or auth_token is None:
            raise django.conf.ImproperlyConfigured(
                'Twilio backend enabled but settings are missing')

        from twilio.rest import Client
        self.client = Client(account_sid, auth_token)

    def send_message(self, from_address, to_addresses, message):
        for address in to_addresses:
            self.client.messages.create(
                to=address, from_=from_address, body=message)

    @classmethod
    def get_default_from_address(cls):
        return settings.TWILIO_FROM_NUMBER
