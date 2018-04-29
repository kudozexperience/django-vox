import typing

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import lxml
import requests
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'json-webhook'
    PROTOCOL = 'json-webhook'
    VERBOSE_NAME = _('Generic Webhook (JSON)')

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
        template = base.template_from_string(html)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        return cls.build_message(subject, body, parameters)

    @classmethod
    def extract_model(cls, message):
        tree = lxml.etree.fromstring(message)
        subject = tree[0].text
        model = {}
        key = ''
        for element in tree[1]:
            if element.tag == 'dt':
                key = element.text
            else:
                model[key] = element.text
        return subject, model

    @classmethod
    def send_message(cls, contact, message):
        subject, model = cls.extract_model(message)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(contact.address, json=model, headers=headers)
        if not response.ok:
            raise RuntimeError(
                'HTTP error: {}'.format(response.text))
