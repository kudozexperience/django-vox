import json

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.core import mail
from django.utils.translation import ugettext_lazy as _

from . import base


class MultipartMessage:

    def __init__(self):
        self.subject = ''
        self.text = ''
        self.html = ''

    @classmethod
    def from_dict(cls, obj):
        result = cls()
        result.subject = obj.get('subject')
        result.text = obj.get('text')
        result.html = obj.get('html')
        return result

    @classmethod
    def from_string(cls, string):
        return cls.from_dict(json.loads(string))

    def to_dict(self):
        return {'subject': self.subject, 'text': self.text, 'html': self.html}

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_mail(self) -> mail.EmailMultiAlternatives:
        email = mail.EmailMultiAlternatives()
        email.subject = self.subject
        if self.text:
            email.body = self.text
            if self.html:
                email.attach_alternative(self.html, 'text/html')
        elif self.html:
            email.body = self.html
            email.content_subtype = 'html'
        return email


class Backend(base.Backend):

    ID = 'email-basic'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Email (Basic)')
    USE_SUBJECT = True

    @classmethod
    def build_multipart(cls, subject: str, body: str,
                        parameters: dict) -> MultipartMessage:
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
        mpm = MultipartMessage.from_string(message)
        email = mpm.to_mail()
        email.from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        email.to = [contact.address]
        connection = django.core.mail.get_connection()
        connection.send_messages([email])
