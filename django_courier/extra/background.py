from background_task import background
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

import django_courier.models


class BackgroundCourierModel(django_courier.models.CourierModel):
    """
    A courier model that sends it's calls though a background task
    """

    class Meta:
        abstract = True

    def issue_notification(self, codename: str,
                           target: django_courier.models.CourierModelN = None,
                           source: django_courier.models.CourierModelN = None):
        kwargs = {}
        self_cls_str = str(self.__class__._meta)
        if target is not None:
            kwargs['target_cls_str'] = str(target.__class__._meta)
            kwargs['target_id'] = target.id
        if source is not None:
            kwargs['source_cls_str'] = str(source.__class__._meta)
            kwargs['source_id'] = source.id
        issue_notification(codename, self_cls_str, self.id, **kwargs)


@background(queue='django-courier')
def issue_notification(
        codename: str,
        content_cls_str: str,
        content_id: int,
        target_cls_str: str = '',
        target_id: int = 0,
        source_cls_str: str = '',
        source_id: int = 0):
    content_model = apps.get_model(content_cls_str)
    content = content_model.objects.get(pk=content_id)
    content_ct = ContentType.objects.get_for_model(content)

    target = None
    if target_cls_str != '':
        model = apps.get_model(target_cls_str)
        target = model.objects.get(pk=target_id)
    source = None
    if target_cls_str != '':
        model = apps.get_model(source_cls_str)
        source = model.objects.get(pk=source_id)

    notification = django_courier.models.Notification.objects.get(
        codename=codename, content_type=content_ct)
    notification.issue(content, target, source)
