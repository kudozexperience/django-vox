import abc
import collections
import inspect
import random
from typing import Any, List, Mapping, TypeVar, cast

import aspy
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import NOT_PROVIDED, Q
from django.template import Context
from django.utils.translation import ugettext_lazy as _

import django_vox.backends
from django_vox.backends.base import AttachmentData

from . import base, registry

__all__ = ('find_activity_type', 'get_model_from_relation',
           'resolve_parameter', 'make_model_preview', 'PreviewParameters',
           'get_model_variables', 'get_model_attachment_choices',
           'AbstractContactable', 'VoxOptions', 'VoxModelBase', 'VoxModel',
           'VoxNotification', 'VoxNotifications', 'VoxAttach',
           'VoxAttachments', 'NotificationManager', 'Notification',
           'Template', 'TemplateAttachment', 'SiteContactManager',
           'SiteContact', 'SiteContactSetting', 'FailedMessage', 'InboxItem')


def find_activity_type(url):
    for item in aspy.__dict__.values():
        if inspect.isclass(item):
            if issubclass(item, (aspy.Object, aspy.Link)):
                if item.get_type() == url:
                    return item


def get_model_from_relation(field):
    # code copied from django's admin
    if not hasattr(field, 'get_path_info'):
        raise RuntimeError('Field is not a relation')
    return field.get_path_info()[-1].to_opts.model


def resolve_parameter(key, parameters):
    remainder, _, last = key.rpartition('.')
    parts = remainder.split('.')
    for part in parts:
        try:
            contains = part in parameters
        except TypeError:
            contains = False
        if contains:
            parameters = parameters[part]
        elif hasattr(parameters, part):
            parameters = getattr(parameters, part)
        else:
            return None
    if hasattr(parameters.__class__, '_vox_meta'):
        meta = parameters.__class__._vox_meta
        if last in meta.attachments:
            return meta.attachments[last].get_data(parameters)
    return None


def make_model_preview(object_type):
    obj = object_type.objects.first()
    if obj is not None:
        return obj
    obj = object_type()
    for field in object_type._meta.fields:
        value = None
        if field.default != NOT_PROVIDED:
            value = field.default
        else:
            desc = str(field.description).lower()
            if desc.startswith('string'):
                value = '{{{}}}'.format(field.verbose_name)
            elif desc.startswith('integer'):
                value = random.randint(1, 100)
            else:
                pass
        setattr(obj, field.attname, value)
    return obj


class PreviewParameters:

    def __init__(self, object_type, actor_type, target_type):
        self.target = (make_model_preview(target_type)
                       if target_type else {})
        self.actor = (make_model_preview(actor_type)
                      if actor_type else {})
        self.contact = base.Contact(
            'Contact Name', 'email', 'contact@example.org')
        self.object = make_model_preview(object_type)
        # for backwards compatibility
        self.source = self.actor
        self.content = self.object

    def __contains__(self, item):
        return item in ('contact', 'target', 'actor', 'object',
                        'content', 'source')

    def __getitem__(self, attr):
        return getattr(self, attr)


def get_model_variables(label, value, cls, ancestors=set()):
    assert issubclass(cls, models.Model)
    sub_ancestors = ancestors.copy()
    sub_ancestors.add(cls)
    attrs = []
    skip_relations = len(ancestors) > 2
    children = []
    for field in cls._meta.fields:
        sub_label = field.verbose_name.title()
        sub_value = '{}.{}'.format(value, field.name)
        if field.is_relation:
            model = get_model_from_relation(field)
            # prevent super long/circular references
            if skip_relations or model in ancestors:
                continue
            children.append(get_model_variables(
                sub_label, sub_value, model, ancestors=sub_ancestors))
        else:
            attrs.append({'label': sub_label, 'value': sub_value})
    return {'label': label, 'value': value, 'attrs': attrs,
            'rels': children}


def get_model_attachment_choices(label, value, cls, ancestors=set()):
    sub_ancestors = ancestors.copy()
    sub_ancestors.add(cls)
    if hasattr(cls, '_vox_meta'):
        fields = cls._vox_meta.attachments
        for field in fields:
            label = ('{}/{}'.format(label, field.label)
                     if label else field.label)
            yield (value + '.' + field.key), label
    if hasattr(cls, '_meta') and len(sub_ancestors) < 3:
        for field in cls._meta.fields:
            if field.is_relation:
                model = get_model_from_relation(field)
                if model not in ancestors:
                    sub_label = field.verbose_name.title()
                    sub_label = ('{}/{}'.format(label, sub_label)
                                 if label else sub_label)
                    sub_value = '{}.{}'.format(value, field.name)
                    yield from get_model_attachment_choices(
                        sub_label, sub_value, field.related_model,
                        ancestors=sub_ancestors)


class AbstractContactable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[base.Contact]:
        ...


class VoxOptions(object):
    """
    Options for Vox extensions
    """

    ALL_OPTIONS = ('notifications', 'attachments')
    # list of notification code names
    notifications = []
    attachments = {}

    def __init__(self, meta):
        """
        Set any options provided, replacing the default values
        """
        if meta is not None:
            for key, value in meta.__dict__.items():
                if key in self.ALL_OPTIONS:
                    setattr(self, key, value)
                elif not key.startswith('_'):  # ignore private parts
                    raise ValueError(
                        'VoxMeta has invalid attribute: {}'.format(key))


class VoxModelBase(models.base.ModelBase):
    """
    Metaclass for Vox extensions.

    Deals with notifications on VoxOptions
    """
    def __new__(mcs, name, bases, attributes):
        new = super(VoxModelBase, mcs).__new__(
            mcs, name, bases, attributes)
        meta = attributes.pop('VoxMeta', None)
        setattr(new, '_vox_meta', VoxOptions(meta))
        return new


VoxModelN = TypeVar('VoxModelN', 'VoxModel', None)


class VoxModel(models.Model, metaclass=VoxModelBase):
    """
    Base class for models that implement notifications
    """

    class Meta:
        abstract = True

    @classmethod
    def get_notification(cls, codename: str) -> 'Notification':
        ct = ContentType.objects.get_for_model(cls)
        return Notification.objects.get(
            codename=codename, object_type=ct)

    def issue_notification(self, codename: str,
                           target: VoxModelN = None,
                           actor: VoxModelN = None):
        notification = self.get_notification(codename)
        notification.issue(self, target, actor)

    def get_activity_object(self, codename, actor, target):
        """Return an aspy.Object object for the activity.

        The parameters actor and target may be None.
        """
        return self.__activity__()

    def get_actor_address(self):
        if self.__class__ not in registry.actors:
            raise RuntimeError(
                '{} is not a registered actor, use '
                'django_vox.registry.actors[{}].set_regex(...)'.format(
                    self, self.__class__))
        url = registry.actors[self.__class__].reverse(self)
        return django_vox.base.full_iri(url)

    def __activity__(self):
        if self.__class__ in registry.actors:
            # this is safer, and probably faster
            iri = self.get_actor_address()
        else:
            iri = django_vox.base.full_iri(self.get_absolute_url())

        return aspy.Object(name=str(self), id=iri)


class VoxNotifications(list):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not isinstance(value, VoxNotification):
                value = VoxNotification(value)
            if not value.params['codename']:
                value.params['codename'] = key
            self.append(value)


class VoxNotification:
    REQUIRED_PARAMS = {'codename', 'description'}
    OPTIONAL_PARAMS = {'actor_type': '', 'target_type': '',
                       'activity_type': '', 'required': False}

    def __init__(self, description, codename='', **kwargs):
        self.params = {
            'codename': codename,
            'description': description,
            'from_code': True,
        }
        for key, default in self.OPTIONAL_PARAMS.items():
            if key in kwargs:
                self.params[key] = kwargs.pop(key)
            else:
                self.params[key] = default
        if kwargs:
            raise ValueError('Unrecognized parameters {}'.format(
                ', '.join(kwargs.keys())))

    def params_equal(self, notification):
        for key in self.params:
            value = getattr(notification, key)
            my_value = self.params[key]
            if key in ('actor_type', 'target_type'):
                if value is None:
                    value = ''
                else:
                    value = '{}.{}'.format(value.app_label, value.model)
            if key == 'action_type':
                value = value.get_type()
            if value != my_value:
                return False
        return True

    def param_value(self, key):
        value = self.params[key]
        if key in ('actor_type', 'target_type'):
            if value == '':
                return None
            model = apps.get_model(value)
            return ContentType.objects.get_for_model(model)
        if key == 'action_type':
            return find_activity_type(value)
        return value

    def set_params(self, notification):
        for key in self.params:
            setattr(notification, key, self.param_value(key))

    def create(self, object_type):
        new = Notification(object_type=object_type)
        self.set_params(new)
        return new

    @property
    def codename(self):
        return self.params['codename']


# Temporarily here for backwards compatibility
class VoxParam(VoxNotification):

    def __init__(self, codename, description, **kwargs):
        super().__init__(description, codename=codename, **kwargs)


class VoxAttach:
    def __init__(self, attr: str=None,
                 mime_attr: str='', mime_string: str='', label=''):
        self.key = ''  # gets set later
        self.attr = attr
        if bool(mime_attr) == bool(mime_string):
            raise RuntimeError(
                'Either mime_attr must be set or mime_string (not both)')
        self.mime_attr = mime_attr
        self.mime_string = mime_string
        self._label = label

    @property
    def label(self):
        return self._label if self._label else self.key

    def get_data(self, model_instance: VoxModel):
        data = getattr(model_instance, self.attr)
        if callable(data):
            data = data()
        # force bytes
        if not isinstance(data, bytes):
            if not isinstance(data, str):
                data = str(data)
            data = data.encode()
        if self.mime_attr:
            mime = getattr(model_instance, self.mime_attr)
            if callable(mime):
                mime = mime()
        else:
            mime = self.mime_string
        return AttachmentData(data, mime)


class VoxAttachments:
    def __init__(self, **kwargs: Mapping[str, VoxAttach]):
        self.items = {}
        for key, value in kwargs.items():
            value.key = key
            if value.attr is None:
                value.attr = key
            self.items[key] = value

    def __iter__(self):
        yield from self.items.values()

    def __contains__(self, item: str):
        return self.items.__contains__(item)

    def __getitem__(self, item: str):
        return self.items.__getitem__(item)


class NotificationManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, app_label, model, codename):
        return self.get(
            codename=codename,
            object_type=ContentType.objects.db_manager(
                self.db).get_by_natural_key(app_label, model),
        )


class Notification(models.Model):
    """
    Base class for all notifications
    """

    codename = models.CharField(_('codename'), max_length=100)
    object_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE,
        limit_choices_to=registry.channel_type_limit,
        verbose_name=_('object type'))
    description = models.TextField(_('description'))
    actor_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE, related_name='+',
        limit_choices_to=registry.channel_type_limit,
        verbose_name=_('actor model'), null=True, blank=True)
    target_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE, related_name='+',
        limit_choices_to=registry.channel_type_limit,
        verbose_name=_('target model'), null=True, blank=True)
    activity_type = models.CharField(_('activity_type'), max_length=500)
    required = models.BooleanField(
        _('required'), default=False,
        help_text=_('If true, triggering the notification will throw an '
                    'error if there is no available template/contact'))
    activity_type = models.URLField(
        _('activity type'), default='', blank=True,
        help_text=_('Full URL for activity type (i.e. '
                    'https://www.w3.org/ns/activitystreams#Object)')
    )
    from_code = models.BooleanField(
        _('from code'), default=False,
        help_text=_('True if the notification is defined in the code and '
                    'automatically managed'))

    objects = NotificationManager()

    def __str__(self):
        return "{} | {} | {}".format(
            self.object_type.app_label, self.object_type, self.codename)

    def natural_key(self):
        return self.object_type.natural_key() + (self.codename,)

    natural_key.dependencies = ['contenttypes.contenttype']

    def get_recipient_models(self):
        recipient_spec = {
            'si': SiteContact,
            're': self.get_target_type(),
            'se': self.get_actor_type(),
            'c': self.get_object_model(),
        }
        return dict((key, value) for (key, value)
                    in recipient_spec.items() if value is not None)

    def get_parameter_models(self):
        spec = {
            'target': self.get_target_type(),
            'actor': self.get_actor_type(),
            'object': self.get_object_model(),
        }
        return dict((key, value) for (key, value)
                    in spec.items() if value is not None)

    def get_recipient_instances(self, obj, target, actor):
        choices = {
            'si': SiteContact(),
            'c': obj,
        }
        if self.target_type and (target is not None):
            choices['re'] = target
        elif self.target_type:
            raise RuntimeError(
                'Model specified "target_type" for notification but '
                'target missing on issue_notification ')
        elif target is not None:
            raise RuntimeError('Recipient added to issue_notification, '
                               'but is not specified in VoxMeta')
        if self.actor_type and (actor is not None):
            choices['se'] = actor
        elif self.actor_type:
            raise RuntimeError(
                'Model specified "actor_type" for notification but actor '
                'missing on issue_notification ')
        elif actor is not None:
            raise RuntimeError('Actor added to issue_notification, but is '
                               'not specified in VoxMeta')

        return dict((key, model) for (key, model)
                    in choices.items() if model is not None)

    def get_recipient_channels(self, obj, target, actor):
        instances = self.get_recipient_instances(obj, target, actor)
        return dict((key, channel)
                    for recip_key, model in instances.items()
                    for key, channel in registry.channels[
                        model.__class__].prefix(recip_key).bind(model).items())

    def get_recipient_choices(self):
        recipient_models = self.get_recipient_models()
        for recipient_key, model in recipient_models.items():
            channel_data = registry.channels[model].prefix(recipient_key)
            for key, channel in channel_data.items():
                yield key, channel.name

    def issue(self, obj: VoxModel,
              target: VoxModelN=None,
              actor: VoxModelN=None):
        """
        To send a notification to a user, get all the user's active methods.
        Then get the backend for each method and find the relevant template
        to send (and has the said notification). Send that template with
        the parameters with the backend.

        :param obj: model object that the notification is about
        :param target: either a user, or None if no logical target
        :param actor: user who initiated the notification
        :return: None
        """
        # check
        parameters = {
            'content': obj,
            'object': obj,
        }
        if target is not None:
            parameters['target'] = target
        if actor is not None:
            parameters['actor'] = actor
            # backwards compatibility
            parameters['source'] = actor

        parameters['activity_object'] = obj.get_activity_object(
            self.codename, actor, target)
        parameters['activity_type'] = self.get_activity_type()

        channels = self.get_recipient_channels(obj, target, actor)
        contactable_list = dict((key, channel.contactables())
                                for (key, channel) in channels.items())

        contact_set = collections.defaultdict(dict)
        for key, contactables in contactable_list.items():
            for c_able in contactables:
                for contact in c_able.get_contacts_for_notification(self):
                    contact_set[key][contact] = c_able

        sent = False
        for key, contact_dict in contact_set.items():
            if self.send_messages(contact_dict, parameters,
                                  Template.objects.filter(recipient=key)):
                sent = True
        if not sent and self.required:
            raise RuntimeError('Notification required, but no message sent')

    def send_messages(
            self, contacts: Mapping[base.Contact, AbstractContactable],
            generic_params: Mapping[str, Any], template_queryset):

        def _get_backend_message(protocol):
            backends = django_vox.registry.backends.by_protocol(protocol)
            # now get all the templates for these backends
            for be in backends:
                tpl = template_queryset.filter(
                    backend=be.ID, notification=self, enabled=True).first()
                if tpl is not None:
                    return be, tpl
            return None

        # per-protocol message cache
        cache = {}
        sent = False
        for contact, contactable in contacts.items():
            params = generic_params.copy()
            params['contact'] = contact
            params['recipient'] = contactable
            params['notification'] = self
            proto = contact.protocol
            if proto not in cache:
                cache[proto] = _get_backend_message(proto)
            if cache[proto] is not None:
                backend, template = cache[proto]
                attachments = []
                if backend.USE_ATTACHMENTS:
                    for attachment in template.attachments.all():
                        data = resolve_parameter(attachment.key, params)
                        if data is not None:
                            attachments.append(data)
                message = backend.build_message(
                    template.subject, template.content, params, attachments)
                # We're catching all exceptions here because some people
                # are bad people and can't subclass properly
                try:
                    backend.send_message(contact, message)
                    sent = True
                except Exception as e:
                    FailedMessage.objects.create(
                        backend=backend.ID,
                        contact_name=contact.name,
                        address=contact.address,
                        message=str(message),
                        error=str(e),
                    )
        return sent

    def can_issue_custom(self):
        return not (self.actor_type or self.target_type)

    def preview(self, backend_id, message):
        backend = registry.backends.by_id(backend_id)
        params = PreviewParameters(
            self.get_object_model(), self.get_actor_type(),
            self.get_target_type())
        return backend.preview_message('', message, params)

    def get_actor_type(self):
        return (self.actor_type.model_class() if self.actor_type_id
                else None)

    def get_target_type(self):
        return (self.target_type.model_class() if self.target_type_id
                else None)

    def get_object_model(self):
        return (self.object_type.model_class() if self.object_type_id
                else None)

    def get_activity_type(self):
        return find_activity_type(self.activity_type)

    def get_recipient_variables(self):
        recipient_spec = self.get_recipient_models()
        actor_type = self.get_actor_type()
        target_type = self.get_target_type()
        content_model = self.get_object_model()
        mapping = {}
        for target_key, model in recipient_spec.items():
            if model is not None:
                channels = registry.channels[model].prefix(target_key)
                for key, channel in channels.items():
                    mapping[key] = get_model_variables(
                        'Recipient', 'recipient', channel.target_class)
        content_name = content_model._meta.verbose_name.title()
        mapping['_static'] = [
            get_model_variables(content_name, 'object', content_model),
        ]
        if actor_type:
            mapping['_static'].append(
                get_model_variables('Actor', 'actor', actor_type))
        if target_type:
            mapping['_static'].append(
                get_model_variables('Target', 'target', target_type))
        return mapping


class Template(models.Model):

    class Meta:
        verbose_name = _('template')

    notification = models.ForeignKey(
        to=Notification, on_delete=models.PROTECT,
        verbose_name=_('notification'))
    backend = models.CharField(_('backend'), max_length=100)
    subject = models.CharField(_('subject'), max_length=500, blank=True)
    content = models.TextField(_('content'))
    recipient = models.CharField(
        verbose_name=_('recipient'), max_length=103, default='re',
        help_text=_('Who this message actually gets sent to.'))
    enabled = models.BooleanField(
        _('enabled'), default=True,
        help_text=_('When not active, the template will be ignored'))

    objects = models.Manager()

    def render(self, parameters: dict, autoescape=True):
        content = cast(str, self.content)
        template = django_vox.backends.base.template_from_string(content)
        context = Context(parameters, autoescape=autoescape)
        return template.render(context)

    def __str__(self):
        choices = {}
        if self.notification:
            choices = dict(self.notification.get_recipient_choices())
        recipient = choices.get(self.recipient, self.recipient)
        backend = registry.backends.by_id(self.backend)
        return '{} for {}'.format(backend.VERBOSE_NAME, recipient)


class TemplateAttachment(models.Model):

    class Meta:
        verbose_name = _('template attachment')

    template = models.ForeignKey(
        to=Template, on_delete=models.CASCADE,
        verbose_name=_('template'), related_name='attachments')
    key = models.CharField(_('key'), max_length=500)


class SiteContactManager(models.Manager, AbstractContactable):
    use_in_migrations = True

    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[base.Contact]:
        wlq = Q(enable_filter='whitelist',
                sitecontactsetting__notification=notification,
                sitecontactsetting__enabled=True)
        blq = Q(enable_filter='blacklist') & ~Q(
                sitecontactsetting__notification=notification,
                sitecontactsetting__enabled=False)
        for sc in SiteContact.objects.filter(blq | wlq).distinct():
            yield base.Contact(sc.name, sc.protocol, sc.address)


# can't make this subclass AbstractContact or fields become unset-able
class SiteContact(VoxModel):

    ENABLE_CHOICES = (
        ('blacklist', _('Blacklist')),
        ('whitelist', _('Whitelist')),
    )

    class Meta:
        verbose_name = _('site contact')
        unique_together = (('address', 'protocol'),)

    name = models.CharField(_('name'), blank=True, max_length=500)
    protocol = models.CharField(_('protocol'), max_length=100)
    address = models.CharField(_('address'), max_length=500, blank=True)
    enable_filter = models.CharField(choices=ENABLE_CHOICES, max_length=10,
                                     default='blacklist')

    objects = SiteContactManager()

    def __str__(self):
        return self.name

    @staticmethod
    def all_contacts(_obj):
        yield SiteContact.objects


registry.channels[SiteContact].add(
    '', '', SiteContact, SiteContact.all_contacts)


class SiteContactSetting(models.Model):

    class Meta:
        verbose_name = _('site contact setting')
        unique_together = (('site_contact', 'notification'),)

    site_contact = models.ForeignKey(SiteContact, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    enabled = models.BooleanField(_('enabled'))

    objects = models.Manager()


class FailedMessage(models.Model):

    class Meta:
        verbose_name = _('failed message')

    backend = models.CharField(_('backend'), max_length=100)
    contact_name = models.CharField(_('contact name'), max_length=500)
    address = models.CharField(_('address'), max_length=500)
    message = models.TextField(_('message'))
    error = models.TextField(_('error'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return '{} @ {}'.format(self.address, self.created_at)

    def resend(self):
        # find backend
        backend = django_vox.registry.backends.by_id(self.backend)
        contact = base.Contact(
            self.contact_name, backend.PROTOCOL, self.address)
        backend.send_message(contact, self.message)
        self.delete()


class InboxItem(models.Model):
    # these two fields tell you who's inbox it is
    owner_id = models.CharField(
        _('owner id'), max_length=2048, db_index=True)
    owner_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE, related_name='+',
        verbose_name=_('owner type'))
    owner = GenericForeignKey('owner_type', 'owner_id')
    # the following fields are denormalized in case you want them
    # for queries
    actor_id = models.CharField(
        _('actor id'), max_length=2048, db_index=True)
    object_id = models.CharField(
        _('object id'), max_length=2048, db_index=True)
    type = models.CharField(
        _('type'), max_length=512, db_index=True)
    # here's where the actual data is stored
    json = models.TextField()
    # and a timestamp, maybe useful
    timestamp = models.DateTimeField(
        _('timestamp'), db_index=True, auto_now_add=True)
