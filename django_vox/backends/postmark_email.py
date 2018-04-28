import typing

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import requests
from django.core.exceptions import ImproperlyConfigured
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

    ID = 'postmark-template'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Postmark Email Templates')
    ENDPOINT = 'https://api.postmarkapp.com/email/withTemplate'
    DEPENDS = ('lxml',)

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
