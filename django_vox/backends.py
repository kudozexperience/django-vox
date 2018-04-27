import collections
import json
import pydoc
import typing

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import requests
from django.core.exceptions import ImproperlyConfigured
from django.template import Context
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from . import settings, templates

PROTOCOLS = {
    'email': _('Email'),
    'sms': _('SMS'),
    'slack-webhook': _('Slack Webhook'),
}

# a global that we initialize once, please use
# `get_backends_from_settings(str)`
__ALL_BACKENDS__ = collections.defaultdict(list)


def html_format(text: str):
    escaped = django.utils.html.escape(text)
    return escaped.replace('\r\n', '<br/>').replace('\n', '<br/>')


class NotificationBackend:

    USE_SUBJECT = False
    ESCAPE_HTML = True

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict):
        template = templates.from_string(body)
        context = Context(parameters, autoescape=cls.ESCAPE_HTML)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        message = cls.build_message(subject, body, parameters)
        if not cls.ESCAPE_HTML:
            message = html_format(message)
        return message

    @classmethod
    def send_message(
            cls, contact: 'django_vox.base.Contact', message):
        raise NotImplementedError


class BasicEmailBackend(NotificationBackend):

    ID = 'email-basic'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Email (Basic)')
    USE_SUBJECT = True

    @classmethod
    def build_multipart(cls, subject: str, body: str,
                        parameters: dict) -> templates.MultipartMessage:
        raise NotImplementedError()

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict):
        return str(cls.build_multipart(subject, body, parameters))

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        parts = cls.build_multipart(subject, body, parameters)
        if parts.html:
            return parts.html
        return django.utils.html.escape(parts.text)

    @classmethod
    def send_message(cls, contact, message):
        mpm = templates.MultipartMessage.from_string(message)
        email = mpm.to_mail()
        email.from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        email.to = [contact.address]
        connection = django.core.mail.get_connection()
        connection.send_messages([email])


class EmailBackend(BasicEmailBackend):

    ID = 'email'
    VERBOSE_NAME = _('Email (Template-based)')

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return templates.email_parts(subject, body, parameters)


class HtmlEmailBackend(BasicEmailBackend):

    ID = 'email-html'
    VERBOSE_NAME = _('Email (HTML)')

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return templates.email_html(subject, body, parameters)


class MarkdownEmailBackend(BasicEmailBackend):

    ID = 'email-md'
    VERBOSE_NAME = _('Email (Markdown)')

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return templates.email_md(subject, body, parameters)


class PostmarkTemplateBackend(NotificationBackend):

    ID = 'postmark-template'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Postmark Email Templates')
    ENDPOINT = 'https://api.postmarkapp.com/email/withTemplate'

    @classmethod
    def parse_message(cls, body: str) -> typing.Mapping[str, str]:
        data = {}
        for line in body.split('\n'):
            parts = line.split(':')
            key = parts[0].strip()
            if key == '':
                continue
            data[key] = (':'.join(parts[1:])).strip()
        return data

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict):
        data = cls.parse_message(body)
        def_list = '\n'.join(
            '<dt>{}</dt><dd>{}</dd>'.format(escape(key), escape(value))
            for key, value in data.items()
        )
        html = '<html>\n<h1>{}</h1>\n<dl>\n{}\n</dl>\n</html>'.format(
            escape(subject), def_list)
        context = django.template.Context(parameters)
        template = templates.from_string(html)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        return cls.build_message(subject, body, parameters)

    @classmethod
    def send_message(cls, contact, message):
        from lxml import etree
        tree = etree.fromstring(message)
        from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        data = {
            'TemplateAlias': tree[0].text,
            'TemplateModel': {},
            'From': from_email,
            'To': contact.address,
        }
        key = ''
        for element in tree[1]:
            if element.tag == 'dt':
                key = element.text
            else:
                data['TemplateModel'][key] = element.text
        token = getattr(django.conf.settings, 'POSTMARK_API_TOKEN', None)
        if token is None:
            raise ImproperlyConfigured(
                'Please set POSTMARK_API_TOKEN in your settings')
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Postmark-Server-Token': token,
        }

        response = requests.post(cls.ENDPOINT, json=data, headers=headers)
        data_result = response.json()
        if not response.ok:
            raise RuntimeError('Postmark error: {} {}'.format(
                data_result['ErrorCode'], data_result['Message']))


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
        _init_backends()  # pragma: no cover
    for backend in __ALL_BACKENDS__[protocol]:
        yield backend


def get_backends():
    if not __ALL_BACKENDS__:
        _init_backends()  # pragma: no cover
    for backend_list in __ALL_BACKENDS__.values():
        for backend in backend_list:
            yield backend


def get_protocol_choices():
    if not __ALL_BACKENDS__:
        _init_backends()  # pragma: no cover
    for protocol in __ALL_BACKENDS__.keys():
        yield (protocol, PROTOCOLS.get(protocol, protocol))
