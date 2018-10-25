import urllib.parse

import aspy
import django.http
import django.shortcuts

from . import models, registry, settings


def get_local_urlpart(full_uri):
    _, _, path, query, fragment = urllib.parse.urlsplit(full_uri)
    return urllib.parse.urlunsplit(('', '', path, query, fragment))


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
        actor = registry.objects.get_local_object(path)
    except registry.ObjectNotFound:
        return django.http.HttpResponseNotFound()
    obj = actor.__activity__()
    obj_id = obj['id']
    for part in ('followers', 'following', 'liked', 'inbox', 'outbox'):
        if part not in obj:
            obj[part] = urllib.parse.urljoin(obj_id, part)

    return django.http.HttpResponse(
        str(obj), content_type='application/activity+json')


@fix_path
def outbox(request, path):
    try:
        owner = registry.objects.get_local_object(path)
    except registry.ObjectNotFound:
        return django.http.HttpResponseNotFound()
    if request.user != owner:
        return django.http.HttpResponseForbidden()
    elif request.method == 'POST':
        return outbox_post(request, owner)
    else:
        return django.http.HttpResponseNotAllowed(
            permitted_methods=('POST',))


@fix_path
def inbox(request, path):
    try:
        owner = registry.objects.get_local_object(path)
    except registry.ObjectNotFound:
        return django.http.HttpResponseNotFound()
    if request.user != owner:
        return django.http.HttpResponseForbidden()
    if request.method == 'GET':
        return inbox_get(request, owner)
    else:
        return django.http.HttpResponseNotAllowed(
            permitted_methods=('GET',))


def inbox_get(_request, owner):
    query = models.InboxItem.objects.select_related('activity').filter(
        owner=owner, read=False).order_by('-id')
    items = []
    for record in query[:settings.INBOX_LIMIT]:
        items.append(record.activity.__activity__())

    collection = aspy.OrderedCollection(
        summary='Inbox for {}'.format(owner),
        items=items)
    return django.http.HttpResponse(
        str(collection), content_type='application/activity+json')


def outbox_post(request, owner):
    obj = request.POST.get('object')
    activity_type = request.POST.get('type')
    if not obj:
        return django.http.HttpResponseBadRequest('Object field required')
    if not activity_type:
        return django.http.HttpResponseBadRequest('Type field required')
    if isinstance(obj, str):
        iri = obj
    elif isinstance(obj, dict):
        iri = obj.get('id')
    else:
        return django.http.HttpResponseBadRequest(
            'Unrecognized format for object')
    if not iri:
        return django.http.HttpResponseBadRequest('Object missing ID')
    # now we have to strip our domain
    local_iri = get_local_urlpart(iri)
    if activity_type == 'Create':
        local_object = registry.objects.create_local_object(local_iri)
    else:
        local_object = registry.objects.get_local_object(local_iri)
    func = 'activity_{}'.format(activity_type.lower())
    method = getattr(local_object, func)
    if method and callable(method):
        method(request.POST, owner)
        return django.http.HttpResponse(status=200, content='')


@fix_path
def empty(_request, _path):
    return django.http.HttpResponse(
        str(aspy.Collection()), content_type='application/activity+json')
