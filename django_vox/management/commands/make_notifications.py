"""
Creates permissions for all installed apps that need permissions.
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, router


class Command(BaseCommand):
    help = 'Creates notifications based on VoxMeta instances in classes'

    def add_arguments(self, parser):  # pragma: no cover
        parser.add_argument(
            '--dry-run',
            action='store_true', dest='dry_run', default=False,
            help='Don\'t actually make changes')

    def handle(self, *args, verbosity=1, dry_run=False, **kwargs):
        for app in apps.get_app_configs():
            make_notifications(app, verbosity=1, dry_run=dry_run)


def make_notifications(app_config, verbosity=1, dry_run=False,
                       using=DEFAULT_DB_ALIAS):
    if not app_config.models_module:
        return

    app_label = app_config.label
    try:
        app_config = apps.get_app_config(app_label)
        contenttype_class = apps.get_model('contenttypes', 'ContentType')
        notification_class = apps.get_model('django_vox', 'Notification')
    except LookupError:
        return

    if not router.allow_migrate_model(using, notification_class):
        return

    # This will hold the notifications we're looking for as
    # (content_type, codename)
    searched_notifications = []
    # The code names and content types that should exist.
    content_types = set()
    for cls in app_config.get_models():
        meta = getattr(cls, '_vox_meta', None)
        if meta is not None:
            # Force looking up the content types in the current database
            # before creating foreign keys to them.
            content_type = contenttype_class.objects.db_manager(
                using).get_for_model(cls)
            content_types.add(content_type)
            for params in meta.notifications:
                searched_notifications.append((content_type, params))

    # Find all the Notification that have a content_type for a model we're
    # looking for.  We don't need to check for code names since we already have
    # a list of the ones we're going to create.
    all_notifications = {}
    for item in notification_class.objects.using(using).filter(
            content_type__in=content_types):
        all_notifications[(item.content_type_id, item.codename)] = item

    new_notifications = []
    for ct, params in searched_notifications:
        notification = all_notifications.get((ct.pk, params.codename))
        if notification is None:
            new_notifications.append(params.create(ct))
        else:
            if not params.params_equal(notification):
                if verbosity > 0:
                    print("Altering notification '%s'" % notification)
                params.set_params(notification)
                if not dry_run:
                    notification.save()
            del all_notifications[(ct.pk, params.codename)]

    if verbosity > 0:
        for notification in new_notifications:
            print("Added notification '%s'" % notification)

    for notification in all_notifications.values():
        if notification.from_code:
            if verbosity > 0:
                print("Removing notification '%s'" % notification)
            if not dry_run:
                notification.delete(using=using)
    if not dry_run:
        notification_class.objects.using(using).bulk_create(new_notifications)
