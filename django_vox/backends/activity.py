import json
from typing import List
from urllib.parse import urlsplit

import aspy
import django.utils.encoding
from django.template import Context
from django.utils.translation import ugettext_lazy as _

import django_vox.base
import django_vox.models
import django_vox.registry

from . import base

__ALL__ = ('make_contact', 'Backend',)


class Backend(base.Backend):

    ID = 'activity'
    PROTOCOL = 'activity'
    VERBOSE_NAME = _('Activity Stream')
    USE_SUBJECT = True
    EDITOR_TYPE = 'html-light'

    # aspy.Create is the default, don't need to use it
    ACTIVITIES = (
        aspy.Accept, aspy.TentativeAccept, aspy.Add, aspy.Delete, aspy.Follow,
        aspy.Ignore, aspy.Join, aspy.Leave, aspy.Like, aspy.Offer, aspy.Invite,
        aspy.Reject, aspy.TentativeReject, aspy.Remove, aspy.Undo, aspy.Update,
        aspy.View, aspy.Listen, aspy.Read, aspy.Move, aspy.Travel,
        aspy.Announce, aspy.Block, aspy.Flag, aspy.Dislike, aspy.Question)
    ACTIVITY_MAP = dict((activity.__name__.lower(), activity)
                        for activity in ACTIVITIES)

    @classmethod
    def _build_summary(cls, body: str, context):
        template = base.template_from_string(body)
        return template.render(context)

    @classmethod
    def _build_subject(cls, subject: str, context):
        if subject == '':
            obj = context.get('object')
            if obj is not None:
                if hasattr(obj, 'name'):
                    if isinstance(obj.name, str):
                        return obj.name
            return ''

        template = base.template_from_string(subject)
        return template.render(context)

    @classmethod
    def _build(cls, subject: str, body: str, parameters: dict):
        context = Context(parameters, autoescape=cls.ESCAPE_HTML)
        return (cls._build_subject(subject, context),
                cls._build_summary(body, context))

    @staticmethod
    def to_activity_object(obj):
        if isinstance(obj, (aspy.Object, aspy.Link)):
            return obj
        if hasattr(obj, '__activity__'):
            return obj.__activity__()
        if hasattr(obj, 'get_absolute_url'):
            return django_vox.base.full_iri(obj.get_absolute_url())
        return None

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict,
                      _attachments: List[base.AttachmentData]):
        subject, summary = cls._build(subject, body, parameters)
        activity_type = parameters.get('activity_type')
        if activity_type is None:
            normalized_codename = parameters['notification'].codename.lower()
            activity_type = cls.ACTIVITY_MAP.get(normalized_codename,
                                                 aspy.Create)
        activity_actor = cls.to_activity_object(parameters.get('actor'))
        activity_target = cls.to_activity_object(parameters.get('target'))
        activity = activity_type(
            name=subject, summary=summary,
            object=parameters['activity_object'],
        )
        if activity_actor is not None:
            activity['actor'] = activity_actor
        if activity_target is not None:
            activity['target'] = activity_target
        return str(activity)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        subject, summary = cls._build(subject, body, parameters)
        return '<div><strong>{}</strong></div>' \
               '<div>{}</div'.format(subject, summary)

    @classmethod
    def add_attachment(cls, data: bytes, mime: str):
        pass  # not supported

    @classmethod
    def send_message(cls, contact: django_vox.base.Contact, message: str):
        url = django.utils.encoding.iri_to_uri(contact.address)
        # I'm pretty sure we're only path matching, but this might change
        path = urlsplit(url)[2]
        # there should be a '/' in the beginning of the path, but that's
        # not normally part of the regex
        if path.startswith('/'):
            path = path[1:]
        # put the message in the relevant inbox
        owner = django_vox.registry.actors.get_local_actor(path)
        json_data = json.loads(message)
        kwargs = {'owner': owner, 'json': message}

        actor_data = json_data.get('actor')
        if isinstance(actor_data, str):
            kwargs['actor_id'] = actor_data
        elif isinstance(actor_data, dict):
            actor_id = actor_data.get('id')
            if actor_id is not None:
                kwargs['actor_id'] = actor_id

        object_data = json_data.get('object')
        if isinstance(object_data, str):
            kwargs['object_id'] = object_data
        elif isinstance(object_data, dict):
            object_id = object_data.get('id')
            if object_id is not None:
                kwargs['object_id'] = object_id

        if 'type' in json_data:
            kwargs['type'] = json_data['type']

        django_vox.models.InboxItem.objects.create(**kwargs)
