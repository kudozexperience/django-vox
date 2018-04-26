import json
from unittest.mock import MagicMock, patch

import django.conf
from django.test import TestCase

from django_courier import backends, base


class TestTwilioBackend(TestCase):

    TEXT = 'Here is a text message \n\n for {{ you }}'
    PARAMS = {'you': 'me'}
    SUBJECT = 'IGNORED'
    MESSAGE = 'Here is a text message \n\n for me'
    PREVIEW = 'Here is a text message <br/><br/> for me'

    @classmethod
    def test_build_message(cls):
        backend = backends.TwilioBackend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        backend = backends.TwilioBackend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        backend = backends.TwilioBackend()
        message = backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS)
        contact = base.Contact('George', 'sms', '+123')
        with patch('twilio.rest.Client'):
            with self.assertRaises(django.conf.ImproperlyConfigured):
                backend.send_message(contact, message)
            with patch('django.conf.settings'):
                backend.send_message(contact, message)
                import twilio.rest
                client = twilio.rest.Client
                assert len(client.mock_calls) > 1
                assert client.mock_calls[0][0] == ''  # class instantiation
                fname, args, kwargs = client.mock_calls[1]
                assert fname == '().messages.create'
                assert args == ()
                assert len(kwargs) == 3
                assert kwargs['to'] == '+123'
                assert isinstance(kwargs['from_'], MagicMock)
                assert kwargs['body'] == self.MESSAGE


class TestTemplateEmailBackend(TestCase):

    TEXT = '{% block text_body%}' \
           'Here is a message \n\n for {{ you }}' \
           '{% endblock %}' \
           '{% block html_body %}' \
           '<p>Here is a message <br/><br/> for {{ you }}' \
           '{% endblock %}' \
                   ''
    PARAMS = {'you': 'me'}
    SUBJECT = 'SUBJECT'
    MESSAGE = {'subject': 'SUBJECT',
               'text': 'Here is a message \n\n for me',
               'html': '<p>Here is a message <br/><br/> for me'}
    PREVIEW = '<p>Here is a message <br/><br/> for me'

    @classmethod
    def test_build_message(cls):
        backend = backends.EmailBackend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        obj = json.loads(message)
        assert cls.MESSAGE == obj

    @classmethod
    def test_preview_message(cls):
        backend = backends.EmailBackend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message
