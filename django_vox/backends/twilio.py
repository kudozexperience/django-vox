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

    @classmethod
    def send_message(cls, from_address, to_addresses, message):
        from twilio.rest import Client
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        if account_sid is None:
            raise django.conf.ImproperlyConfigured(
                'Twilio backend enabled but settings are missing')

        client = Client(account_sid, auth_token)
        for address in to_addresses:
            client.messages.create(
                to=address, from_=from_address, body=message)

    @staticmethod
    def get_default_from_address():
        return settings.TWILIO_FROM_NUMBER
