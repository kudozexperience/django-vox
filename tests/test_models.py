from bs4 import BeautifulSoup
from django.core import mail
from django.test import Client, TestCase

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
        # mail.outbox is a list of EmailMultiAlternatives
        assert len(mail.outbox) == 2
        mail_by_subject = {}
        for message in mail.outbox:
            mail_by_subject[message.subject] = message
        site_mail = mail_by_subject['Site sub email']
        assert site_mail.content_subtype == 'html'
        soup = BeautifulSoup(site_mail.body, 'html.parser')
        anchors = soup.find_all('a')
        assert len(anchors) == 1
        url = anchors[0].get('href')
        assert url.startswith('http://127.0.0.1:8000/2/?token=')
        assert len(url) > 31  # if less, token is blank
        client = Client()
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/html; charset=utf-8'
        author_mail = mail_by_subject['Author sub email']
        assert author_mail.to[0] == 'authorsubscriber@example.org'
        # TODO: continue
        # soup = BeautifulSoup(response.body, 'html.parser')
