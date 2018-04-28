import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'twilio'
    PROTOCOL = 'sms'
    ESCAPE_HTML = False
    VERBOSE_NAME = _('Twilio')
    DEPENDS = ('twilio',)

    @classmethod
    def send_message(cls, contact, message):
        from twilio.rest import Client
        if not hasattr(django.conf.settings, 'TWILIO_ACCOUNT_SID'):
            raise django.conf.ImproperlyConfigured(
                'Twilio backend enabled but TWILIO_* settings missing')
        account_sid = django.conf.settings.TWILIO_ACCOUNT_SID
        auth_token = django.conf.settings.TWILIO_AUTH_TOKEN
        from_number = django.conf.settings.TWILIO_FROM_NUMBER
        client = Client(account_sid, auth_token)
        client.messages.create(
            to=contact.address, from_=from_number, body=message)
