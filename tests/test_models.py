from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import Client, TestCase

import django_vox.models
import django_vox.registry

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
        assert len(mail.outbox) == 3
        for message in mail.outbox:
            # ignore site message
            if 'admin@example.org' in message.to:
                continue
            assert (message.content_subtype == 'plain'
                    and message.mixed_subtype == 'mixed')
            html = message.alternatives[0][0]
            soup = BeautifulSoup(html, 'html.parser')
            anchors = soup.find_all('a')
            assert len(anchors) == 1
            url = anchors[0].get('href')
            assert url.startswith('http://127.0.0.1:8000/2/?token=')
            assert len(url) > 31  # if less, token is blank
            client = Client()
            response = client.get(url)
            assert response.status_code == 200
            assert response['Content-Type'] == 'text/html; charset=utf-8'
            # TODO: continue

    @staticmethod
    def test_markdown():
        # sanity
        assert len(mail.outbox) == 0
        # get the article created template
        template = django_vox.models.Template.objects.get(pk=1)
        template.backend = 'email-md'
        template.subject = 'Hi {{ recipient.name }}'
        template.content = 'Hi {{ recipient.name }},\n\nA new article, ' \
                           '[{{ content }}](http://127.0.0.1:8000/{{ ' \
                           'content.pk }}/?token={{ recipient.get_token | ' \
                           'urlencode }}), has been published at the ' \
                           'awesome blog.'
        template.save()
        # first we create an article as the author user
        author = models.User.objects.get(email='author@example.org')
        models.Article.objects.create(
            author=author,
            title='A second article',
            content='Whoever thought we\'d come this far',
        )
        # now a notification should be fired, check the outbox
        # mail.outbox is a list of EmailMultiAlternatives
        assert len(mail.outbox) == 3
        mail_by_subject = {}
        for message in mail.outbox:
            mail_by_subject[message.subject] = message
        site_mail = mail_by_subject['Hi Subscriber']
        assert len(site_mail.alternatives) == 1
        soup = BeautifulSoup(site_mail.alternatives[0][0], 'html.parser')
        anchors = soup.find_all('a')
        assert len(anchors) == 1
        url = anchors[0].get('href')
        assert url.startswith('http://127.0.0.1:8000/2/?token=')
        assert len(url) > 31  # if less, token is blank

    @staticmethod
    def test_choices():
        """
        Test the values of the dropdown fields
        """
        expected_ids = set()
        for model in (models.Article, models.Subscriber, models.User,
                      models.Comment, django_vox.models.SiteContact):
            ct = ContentType.objects.get_for_model(model)
            expected_ids.add(ct.id)

        vox_ct_limit = django_vox.registry.channel_type_limit()
        assert 'id__in' in vox_ct_limit
        actual_ids = set(vox_ct_limit['id__in'])
        assert actual_ids == expected_ids

    @staticmethod
    def test_previews():
        pp = django_vox.models.PreviewParameters(
            models.Article, models.User, models.Subscriber)
        assert 'recipient' not in pp
        assert 'target' in pp
        assert pp['contact'].name == 'Contact Name'
        assert pp['content'].title == 'Why are there so many blog demos'
        assert pp['target'].name == 'Subscriber'
        assert pp['source'].name == 'Author'
