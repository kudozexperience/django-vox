import collections
import json
import pydoc

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import requests
from django.utils.translation import ugettext_lazy as _

from . import settings, templates

PROTOCOLS = {
    'email',
    'sms',
    'slack',
}

# a global that we initialize once, please use
# `get_backends_from_settings(str)`
__ALL_BACKENDS__ = collections.defaultdict(list)


class NotificationBackend:

    ESCAPE_HTML = True

    @classmethod
    def build_message(
            cls, template: 'django_courier.models.Template', parameters: dict):
        return template.render(parameters, autoescape=cls.ESCAPE_HTML)

    @classmethod
    def send_message(
            cls, contact: 'django_courier.models.IContact', message):
        raise NotImplementedError


class EmailBackend(NotificationBackend):

    ID = 'email'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Email')

    @staticmethod
    def get_backend() -> 'django.core.mail.backends.base.BaseEmailBackend':
        return django.core.mail.backends.smtp.EmailBackend()

    @classmethod
    def build_message(cls, template, parameters):
        return str(templates.email_parts_from_string(
            template.content, parameters))

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
    VERBOSE_NAME = _('Postmark Email')

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
    ESCAPE_HTML = False
    VERBOSE_NAME = _('Twilio')

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
    ESCAPE_HTML = False
    VERBOSE_NAME = _('Slack')

    @classmethod
    def send_message(cls, contact, message):
        data = json.dumps({'text': message})
        headers = {'Content-Type': 'application/json'}
        result = requests.post(contact.address, data=data, headers=headers)
        if not result.ok:
            raise requests.HTTPError(result.text)


def _init_backends():
    """
    Intialize backend settings
    """
    for name in settings.BACKENDS:
        cls = pydoc.locate(name)
        __ALL_BACKENDS__[cls.PROTOCOL].append(cls)


def get_backends_from_settings(protocol: str):
    if not __ALL_BACKENDS__:
        _init_backends()

    for backend in __ALL_BACKENDS__[protocol]:
        yield backend


def get_backend_choices():
    if not __ALL_BACKENDS__:
        _init_backends()
    backends = []
    for backend_list in __ALL_BACKENDS__.values():
        for backend in backend_list:
            backends.append(backend)

    return ((bk.ID, bk.VERBOSE_NAME) for bk in backends)
