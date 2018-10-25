import json

import aspy
from django.test import Client, TestCase

import django_vox.models
import django_vox.settings
from tests import models

EXTRA = {'HTTP_ACCEPT': 'application/activity+json'}


class WebTests(TestCase):
    """Test the walkthrough in the documentation"""

    fixtures = ['test']

    @staticmethod
    def test_actor_page():
        client = Client()
        response = client.get('/~1/', **EXTRA)
        assert 200 == response.status_code
        assert 'application/activity+json' == response['Content-Type']
        json_obj = json.loads(response.content)
        assert 'Person' == json_obj['type']
        assert 'http://127.0.0.1/~1/' == json_obj['id']

    @staticmethod
    def test_article_add():
        # sanity check
        assert django_vox.models.InboxItem.objects.count() == 0
        article = models.Article.objects.get(id=1)
        subscriber = models.Subscriber.objects.get(id=1)
        author_subscriber = models.Subscriber.objects.get(id=2)
        # first we create an article as the author user
        models.Comment.objects.create(
            article=article,
            poster=subscriber,
            content='First Post!11',
        )
        models.Comment.objects.create(
            article=article,
            poster=author_subscriber,
            content='This is why we can\'t have nice things',
        )
        # now two notification should have been fired, check the
        # inbox items
        assert 2 == django_vox.models.InboxItem.objects.count()
        # now, let's check the results of the inbox endpoint
        client = Client()

        # fist we have to authenticate
        response = client.post('/admin/login/',
                               {'username': 'author@example.org',
                                'password': 'password'})
        assert 302 == response.status_code, 'login failed'
        response = client.get('/~1/inbox', **EXTRA)
        assert 200 == response.status_code
        assert 'application/activity+json' == response['Content-Type']
        json_obj = json.loads(response.content)
        assert 'OrderedCollection' == json_obj['type']
        items = json_obj['items']
        assert 2 == len(items)
        # in make sure this is in descending order
        assert 'http://127.0.0.1/1/#comment-1' == items[1]['object']['id']
        assert 'First Post!11' == items[1]['object']['content']
        assert 'Note' == items[1]['object']['name']
        assert 'http://127.0.0.1/1/#comment-2' == items[0]['object']['id']
        assert 'Author Subscriber' == items[0]['actor']['name']

    @staticmethod
    def test_activity_read():
        # sanity check
        assert django_vox.models.InboxItem.objects.count() == 0
        article = models.Article.objects.get(id=1)
        subscriber = models.Subscriber.objects.get(id=1)
        # first we create an article as the author user
        models.Comment.objects.create(
            article=article,
            poster=subscriber,
            content='read me',
        )
        # now one notification should have been fired, check the
        # inbox items
        assert 1 == django_vox.models.InboxItem.objects.count()
        # now we'll check the activity
        client = Client()
        response = client.post('/admin/login/',
                               {'username': 'author@example.org',
                                'password': 'password'})
        assert 302 == response.status_code, 'login failed'
        # make sure inbox looks normal
        response = client.get('/~1/inbox', **EXTRA)
        assert 200 == response.status_code
        assert 'application/activity+json' == response['Content-Type']
        json_obj = json.loads(response.content)
        assert 'OrderedCollection' == json_obj['type']
        items = json_obj['items']
        assert 1 == len(items)
        item_id = items[0]['id']
        # now mark the message as read
        activity = aspy.Read(object=item_id)
        response = client.post('/~1/inbox', activity.to_dict(), **EXTRA)
        assert 200 == response.status_code
        # now we should have one read item
        inbox = django_vox.models.InboxItem.objects.all()
        assert 1 == len(inbox)
        assert True, inbox[0].read
