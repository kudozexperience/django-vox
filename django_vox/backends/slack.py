import json

import requests
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ('Backend',)


class Backend(base.Backend):

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
