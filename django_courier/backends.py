import pydoc
import collections
import requests
import json

from django.core.mail import send_mail
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.conf
import django.template
from . import templates, settings


PROTOCOLS = {
    'email',
    'sms',
    'slack',
}

# a global that we initialize once, please use `get_backends_from_settings(str)`
__ALL_BACKENDS__ = collections.defaultdict(list)


class NotificationBackend:

    @classmethod
    def build_message(cls, template, parameters) -> str:
        return template.render(parameters)

    @classmethod
    def send_message(
            cls, contact: 'django_courier.models.IContact', message: str):
        raise NotImplementedError


class EmailBackend(NotificationBackend):

    ID = 'email'
    PROTOCOL = 'email'

    @staticmethod
    def get_backend() -> 'django.core.mail.backends.base.BaseEmailBackend':
        return django.core.mail.backends.smtp.EmailBackend()

    @classmethod
    def build_message(cls, template, parameters) -> str:
        return str(templates.parts_from_string(template.content, parameters))

    @classmethod
    def send_message(cls, contact, message):
        mpm = templates.MultipartMessage.from_string(message)
        backend = cls.get_backend()
        email = mpm.to_mail()
        email.from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        email.to = [contact.address]
        backend.send_messages([email])


class PostmarkTemplateBackend(EmailBackend):

    ID = 'postmark_template'

    @staticmethod
    def get_backend():
        pass
        # import anymail.backends.postmark
        # return anymail.backends.postmark.EmailBackend()

    @classmethod
    def send(cls, template, contact, parameters):
        from anymail.message import AnymailMessage
        backend = cls.get_backend()
        from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        to_email = [contact.address]
        email = AnymailMessage('', '', from_email, to_email)
        email.template_id = template.content
        email.merge_global_data = parameters
        backend.send_messages([email])


class TwilioBackend(NotificationBackend):

    ID = 'twilio'
    PROTOCOL = 'sms'

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


class SlackWebhookBackend(NotificationBackend):

    ID = 'slack-webhook'
    PROTOCOL = 'slack-webhook'

    @classmethod
    def send_message(cls, contact, message):
        data = json.dumps({'text': message})
        headers = {'Content-Type': 'application/json'}
        requests.post(contact.address, data=data, headers=headers)
        # TODO: check response from the last method


def get_backends_from_settings(protocol: str):
    # let's try to only initialize this once
    if not __ALL_BACKENDS__:
        for name in settings.BACKENDS:
            cls = pydoc.locate(name)
            __ALL_BACKENDS__[cls.PROTOCOL].append(cls)

    for backend in __ALL_BACKENDS__[protocol]:
        yield backend

