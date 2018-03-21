from bs4 import BeautifulSoup
from django.core import mail
from django.test import TestCase, Client

from . import models


class DemoTests(TestCase):
    """Test the walkthrough in the documentation"""

    fixtures = ['test']

    @staticmethod
    def test_walkthrough():
        # sanity
        assert len(mail.outbox) == 0
        # first we create an article as the author user
        author = models.User.objects.get(email='author@example.org')
        models.Article.objects.create(
            author=author,
            title='A second article',
            content='Whoever thought we\'d come this far',
        )
        # now a notification should be fired, check the outbox
        assert len(mail.outbox) == 1
        last_mail = mail.outbox[0]  # EmailMultiAlternatives
        assert last_mail.content_subtype == 'html'
        soup = BeautifulSoup(last_mail.body, 'html.parser')
        anchors = soup.find_all('a')
        assert len(anchors) == 1
        url = anchors[0].get('href')
        assert url.startswith('http://127.0.0.1:8000/2/?token=')
        client = Client()
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/html; charset=utf-8'
        # TODO: continue
        # soup = BeautifulSoup(response.body, 'html.parser')
