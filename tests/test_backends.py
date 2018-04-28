import json
from unittest.mock import MagicMock, patch

import django.conf
from django.test import TestCase

import django_vox.backends.postmark_email
import django_vox.backends.template_email
import django_vox.backends.twilio
from django_vox import base


def mocked_requests_post(url, _data=None, json=None, **_kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        @property
        def ok(self):
            return self.status_code // 100 == 2

    if url == django_vox.backends.postmark_email.Backend.ENDPOINT:
        if not (json.get('TemplateAlias') or json.get('TemplateId')):
            return MockResponse(
                {'ErrorCode': "403", 'Message': 'details'}, 422)
        else:
            return MockResponse({
                "To": "george@example.org",
                "SubmittedAt": "2014-02-17T07:25:01.4178645-05:00",
                "MessageID": "0a129aee-e1cd-480d-b08d-4f48548ff48d",
                "ErrorCode": 0, "Message": "OK"}, 200)
    return MockResponse(None, 404)


class TestTwilioBackend(TestCase):

    TEXT = 'Here is a text message \n\n for {{ you }}'
    PARAMS = {'you': 'me'}
    SUBJECT = 'IGNORED'
    MESSAGE = 'Here is a text message \n\n for me'
    PREVIEW = 'Here is a text message <br/><br/> for me'

    @classmethod
    def test_build_message(cls):
        backend = django_vox.backends.twilio.Backend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        backend = django_vox.backends.twilio.Backend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        backend = django_vox.backends.twilio.Backend()
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


class TestPostmarkBackend(TestCase):

    TEXT = 'line 1 : {{ line_1 }}\n' \
           'line 2 : {{ line_2 }}\n' \
           'line 3 : {{ line_3 }}\n' \
           'line 4 : {{ line_4 }}\n' \
           '\n\n' \
           'c\'est vide'
    PARAMS = {
        'line_1': 'poisson un', 'line_2': 'poisson deux',
        'line_3': 'poisson rouge', 'line_4': 'poisson bleu'}
    SUBJECT = 'SUBJECT'
    MESSAGE = '<html>\n' \
              '<h1>SUBJECT</h1>\n' \
              '<dl>\n' \
              '<dt>line 1</dt><dd>poisson un</dd>\n' \
              '<dt>line 2</dt><dd>poisson deux</dd>\n' \
              '<dt>line 3</dt><dd>poisson rouge</dd>\n' \
              '<dt>line 4</dt><dd>poisson bleu</dd>\n' \
              '<dt>c&#39;est vide</dt><dd></dd>\n' \
              '</dl>\n' \
              '</html>'
    PREVIEW = MESSAGE

    @classmethod
    def test_build_message(cls):
        backend = django_vox.backends.postmark_email.Backend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        backend = django_vox.backends.postmark_email.Backend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        backend = django_vox.backends.postmark_email.Backend()
        bad_message = backend.build_message('', self.TEXT, self.PARAMS)
        message = backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS)
        contact = base.Contact('George', 'email', 'george@example.org')
        with patch('requests.post', side_effect=mocked_requests_post):
            with self.assertRaises(django.conf.ImproperlyConfigured):
                backend.send_message(contact, message)
            with self.settings(POSTMARK_API_TOKEN='token'):
                with self.assertRaises(RuntimeError):
                    backend.send_message(contact, bad_message)
                backend.send_message(contact, message)
                import requests
                assert requests.post.mock_calls[1][2]['json'][
                    'TemplateModel']['line 1'] == 'poisson un'


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
        backend = django_vox.backends.template_email.Backend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        obj = json.loads(message)
        assert cls.MESSAGE == obj

    @classmethod
    def test_preview_message(cls):
        backend = django_vox.backends.template_email.Backend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message
