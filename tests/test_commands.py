import os

from django.apps import AppConfig
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

import tests.models
from django_vox.management.commands import make_notifications
from django_vox.models import Notification


class MakeNotificationTests(TestCase):

    @staticmethod
    def test_kill_orphans():
        """If you completely remove a class,
        its notification should get deleted."""
        cmd = make_notifications.Command()
        cmd.handle(verbose=True)
        assert 3 == Notification.objects.all().count()
        # simulate a deleted class
        fake_ct = ContentType.objects.create(
            app_label='django_vox', model='deleted')
        Notification.objects.create(
            codename='foo', object_type=fake_ct, from_code=True)
        cmd.handle(verbose=True)
        assert 3 == Notification.objects.all().count()

    @staticmethod
    def test_make_notifications():
        cmd = make_notifications.Command()
        assert 0 == Notification.objects.all().count()
        # dry run
        cmd.handle(dry_run=True)
        assert 0 == Notification.objects.all().count()
        # test basic notification making
        cmd.handle(verbose=True)
        assert 3 == Notification.objects.all().count()
        # gather some general things
        article_ct = ContentType.objects.get_for_model(
            tests.models.Article)
        user_ct = ContentType.objects.get_for_model(
            tests.models.User)

        # make a notification to delete
        Notification.objects.create(
            codename='foo',
            object_type=article_ct,
            from_code=True,
        )
        assert Notification.objects.all().count() == 4
        cmd.handle()
        assert Notification.objects.all().count() == 3
        # here's one that shouldn't get deleted
        Notification.objects.create(
            codename='foo',
            object_type=article_ct,
            from_code=False,
        )
        assert Notification.objects.all().count() == 4
        cmd.handle()
        assert Notification.objects.all().count() == 4
        # now we'll change one and it should get reverted
        acn = Notification.objects.get_by_natural_key(
            'tests', 'article', 'create')
        acn.object_model = user_ct
        acn.save()
        cmd.handle(verbose=True)
        acn = Notification.objects.get_by_natural_key(
            'tests', 'article', 'create')
        assert acn.actor_type is not None

    @staticmethod
    def test_bad_appconfig():
        config = AppConfig('os', os)
        make_notifications.make_notifications(config)
