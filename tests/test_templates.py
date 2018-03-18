from django.test import TestCase

from django_courier import models, templates


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


class EmailRenderTests(TestCase):

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
