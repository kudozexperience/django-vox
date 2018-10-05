import json
import urllib.parse

import aspy
import django.http
import django.shortcuts
from django.contrib.contenttypes.models import ContentType

from . import models, registry, settings


def fix_path(func):
    """
    Django likes to strip the trailing slash, but we need it for
    further matching
    """
    def inner(request, path):
        path += '/'
        return func(request, path)

    return inner


@fix_path
def endpoint(_request, path):
    try:
        actor = registry.actors.get_local_actor(path)
    except registry.ActorNotFound:
        return django.http.HttpResponseNotFound()
    obj = actor.__activity__()
    obj_id = obj['id']
    for part in ('followers', 'following', 'liked', 'inbox', 'outbox'):
        if part not in obj:
            obj[part] = urllib.parse.urljoin(obj_id, part)

    return django.http.HttpResponse(
        str(obj), content_type='application/activity+json')


@fix_path
def inbox(request, path):
    try:
        owner = registry.actors.get_local_actor(path)
    except registry.ActorNotFound:
        return django.http.HttpResponseNotFound()
    if not ((settings.VIEW_OWN_INBOX and (request.user == owner)) or
            request.user.has_perm('django_vox.view_inbox', owner)):
        return django.http.HttpResponseForbidden()

    ct = ContentType.objects.get_for_model(owner.__class__)
    query = models.InboxItem.objects.filter(
        owner_type=ct, owner_id=owner.id).order_by('-id')
    items = [json.loads(item.json) for item in query[:settings.INBOX_LIMIT]]
    collection = aspy.OrderedCollection(
        summary='Inbox for {}'.format(owner),
        items=items)
    return django.http.HttpResponse(
        str(collection), content_type='application/activity+json')


@fix_path
def empty(_request, _path):
    return django.http.HttpResponse(
        str(aspy.Collection()), content_type='application/activity+json')
