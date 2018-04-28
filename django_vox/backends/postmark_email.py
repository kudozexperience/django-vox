import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import requests
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from . import json_webhook

__all__ = ('Backend',)


class Backend(json_webhook.Backend):

    ID = 'postmark-template'
    PROTOCOL = 'email'
    VERBOSE_NAME = _('Email (Postmark Templates)')
    ENDPOINT = 'https://api.postmarkapp.com/email/withTemplate'

    @classmethod
    def send_message(cls, contact, message):
        from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        subject, model = cls.extract_model(message)
        data = {
            'TemplateAlias': subject,
            'TemplateModel': model,
            'From': from_email,
            'To': contact.address,
        }
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
