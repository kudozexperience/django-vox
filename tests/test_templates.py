from django.template import TemplateSyntaxError
from django.test import TestCase

from django_courier import models, templates


class MultipartMessageTests(TestCase):

    def test_all(self):
        dict = {
            'subject': 'foo',
            'text': 'A message about foo',
            'html': 'A <blink>message</blink> about foo',
        }
        mpm = templates.MultipartMessage.from_dict(dict)
        new_dict = mpm.to_dict()
        assert new_dict == dict
        serialized = str(mpm)
        new_mpm = templates.MultipartMessage.from_string(serialized)
        assert new_mpm.subject == mpm.subject
        assert new_mpm.text == mpm.text
        assert new_mpm.html == mpm.html
        # test to mail with both text & html
        mail = mpm.to_mail()
        assert mail.body == dict['text']
        assert mail.subject == dict['subject']
        assert len(mail.alternatives) == 1
        content, mime = mail.alternatives[0]
        assert content == dict['html']
        assert mime == 'text/html'
        # test to mail with text only
        mpm.html = ''
        mail = mpm.to_mail()
        assert mail.content_subtype == 'plain'
        assert mail.body == dict['text']
        # test to mail with html only
        mpm.html = dict['html']
        mpm.text = ''
        mail = mpm.to_mail()
        assert mail.content_subtype == 'html'
        assert mail.body == dict['html']


class TemplateRender(TestCase):

    @staticmethod
    def test_blank():
        assert '' == models.Template(content='').render({})

    @staticmethod
    def test_non_html():
        template = models.Template(content='{{ param }}')
        assert 'A&W' == template.render({'param': 'A&W'}, autoescape=False)

    @staticmethod
    def test_html():
        template = models.Template(content='{{ param }}')
        assert 'A&amp;W' == template.render({'param': 'A&W'})

    def test_syntax_error(self):
        template = models.Template(content='{% extends "%}')
        self.assertRaises(TemplateSyntaxError, lambda: template.render({}))

    @staticmethod
    def test_syntax_bad_format():
        template = models.Template(content='{{ }')
        assert '{{ }' == template.render({'param': 'A&W'})

    @staticmethod
    def test_param_missing():
        template = models.Template(content='{{ param }}')
        assert '' == template.render({})


class EmailRenderTests(TestCase):

    @staticmethod
    def test_no_parts():
        params = {'message': 'There\'s a new burger at A&W'}
        email = "Hi, John Doe, here is a message: {{ message }}"
        text = "Hi, John Doe, here is a message: There's a new burger at A&W"
        result = templates.email_parts_from_string(email, params)
        assert result.subject == ''
        assert result.text == text

    @staticmethod
    def test_basic():
        params = {'message': 'There\'s a new burger at A&W'}
        email = """{% block subject %}Test subject{% endblock %}
        {% block text_body %}
        Hi, John Doe, here is a message: {{ message }}
        {% endblock %}
        {% block html_body %}
        <p>Hi, John Doe, here is a message: {{ message }}</p>
        {% endblock %}
        """
        text = "Hi, John Doe, here is a message: There's a new burger at A&W"
        html = "<p>Hi, John Doe, here is a message: " \
               "There&#39;s a new burger at A&amp;W</p>"
        result = templates.email_parts_from_string(email, params)
        assert result.subject == 'Test subject'
        assert result.text == text
        assert result.html == html
