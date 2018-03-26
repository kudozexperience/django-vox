import abc
import collections
from typing import Any, Iterable, List, Mapping, Set, TypeVar, cast

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from . import settings, templates
from .backends import get_backends_from_settings

__ALL_TARGETS__ = collections.OrderedDict()


class CourierOptions(object):
    """
    Options for Courier extensions
    """

    ALL_OPTIONS = ('notifications',)
    # list of notification code names
    notifications = []

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
                        'CourierMeta has invalid attribute: {}'.format(key))


class CourierModelBase(models.base.ModelBase):
    """
    Metaclass for Courier extensions.

    Deals with notifications on CourierOptions
    """
    def __new__(mcs, name, bases, attributes):
        new = super(CourierModelBase, mcs).__new__(
            mcs, name, bases, attributes)
        meta = attributes.pop('CourierMeta', None)
        setattr(new, '_courier_meta', CourierOptions(meta))
        return new


class CourierModel(models.Model, metaclass=CourierModelBase):
    """
    Base class for models that implement notifications
    """

    class Meta:
        abstract = True

    def issue_notification(self, codename: str,
                           recipient: 'AbstractContactNetworkN' = None,
                           sender: 'AbstractContactNetworkN' = None):
        ct = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(
            codename=codename, content_type=ct)
        notification.issue(self, recipient, sender)


class Contact:
    """A generic contact object

    If you want to return something that looks like this, make sure
    to implement the __hash__ method the same, otherwise filtering
    duplicate contacts won't work
    """

    def __init__(self, name: str, protocol: str, address: str, obj: Any=None):
        self.name = name
        self.protocol = protocol
        self.address = address
        self.object = obj

    def __str__(self):
        return '{} <{}:{}>'.format(self.name, self.protocol, self.address)

    def __hash__(self):
        return hash(str(self))


class AbstractContactable(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[Contact]:
        ...


class AbstractContactNetwork(metaclass=abc.ABCMeta):

    def get_contactables(self, channel: str) -> List[AbstractContactable]:
        ...


class ContactNetwork:

    def get_contactables(self, channel: str) -> Iterable[AbstractContactable]:
        if channel == '':
            return (self,)
        raise ValueError('Channel {} not supported'.format(channel))


AbstractContactable.register(ContactNetwork)
AbstractContactNetwork.register(ContactNetwork)


AbstractContactNetworkN = TypeVar('AbstractContactNetworkN',
                                  AbstractContactNetwork, None)


class NotificationManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, app_label, model, codename):
        return self.get(
            codename=codename,
            content_type=ContentType.objects.db_manager(
                self.db).get_by_natural_key(app_label, model),
        )


class CourierParam:
    REQUIRED_PARAMS = {'codename', 'description'}
    OPTIONAL_PARAMS = {'use_recipient': True, 'use_sender': True}

    def __init__(self, codename, description, **kwargs):
        self.params = {
            'codename': codename,
            'description': description,
        }
        for key, default in self.OPTIONAL_PARAMS.items():
            if key in kwargs:
                self.params[key] = kwargs[key]
                del kwargs[key]
            else:
                self.params[key] = default

    def params_equal(self, notification):
        for key in self.params:
            if getattr(notification, key) != self.params[key]:
                return False
        return True

    def set_params(self, notification):
        for key in self.params:
            setattr(notification, key, self.params[key])

    def create(self, content_type):
        new = Notification(content_type=content_type)
        self.set_params(new)
        return new

    @property
    def codename(self):
        return self.params['codename']


class Notification(models.Model):
    """
    Base class for all notifications
    """

    codename = models.CharField(_('codename'), max_length=100)
    content_type = models.ForeignKey(
        to=ContentType, on_delete=models.CASCADE,
        verbose_name=_('content type'))
    description = models.TextField(_('description'))
    use_sender = models.BooleanField(_('use sender'))
    use_recipient = models.BooleanField(_('use recipient'))

    objects = NotificationManager()

    def __str__(self):
        return "{} | {} | {}".format(
            self.content_type.app_label, self.content_type, self.codename)

    def natural_key(self):
        return self.content_type.natural_key() + (self.codename,)

    natural_key.dependencies = ['contenttypes.contenttype']

    def issue(self, content,
              recipient: AbstractContactNetworkN=None,
              sender: AbstractContactNetworkN=None):
        """
        To send a notification to a user, get all the user's active methods.
        Then get the backend for each method and find the relevant template
        to send (and has the said notification). Send that template with
        the parameters with the backend.

        :param content: model object that the notification is about
        :param recipient: either a user, or None if no logical recipient
        :param sender: user who initiated the notification
        :return: None
        """
        # check
        parameters = {
            'content': content,
        }
        networks = {}
        if self.use_recipient and (recipient is not None):
            networks['re'] = recipient
            parameters['recipient'] = recipient
        elif self.use_recipient:
            raise RuntimeError(
                'Model specified "use_recipient" for notification but '
                'recipient missing on issue_notification ')
        elif recipient is not None:
            raise RuntimeError('Recipient added to issue_notification, '
                               'but is not specified in CourierMeta')

        if self.use_sender and (sender is not None):
            networks['se'] = sender
            parameters['sender'] = sender
        elif self.use_sender:
            raise RuntimeError(
                'Model specified "use_sender" for notification but sender '
                'missing on issue_notification ')
        elif sender is not None:
            raise RuntimeError('Sender added to issue_notification, but is '
                               'not specified in CourierMeta')

        contactable_list = {
            'si': (SiteContact.objects,),
        }
        for key, network in networks.items():
            for channel in settings.CHANNELS:
                if channel != '':
                    key = key + ':' + channel
                contactable_list[key] = network.get_contactables(channel)

        contact_set = collections.defaultdict(set)
        for key, contactables in contactable_list.items():
            for c_able in contactables:
                for contact in c_able.get_contacts_for_notification(self):
                    contact_set[key].add(contact)

        for key, contacts in contact_set.items():
            self.send_messages(
                contacts,
                parameters,
                Template.objects.filter(target=key))

    def send_messages(
            self, contacts: Set[Contact],
            generic_params: Mapping[str, Any], template_queryset):

        def _get_backend_message(protocol):
            backends = get_backends_from_settings(protocol)
            # now get all the templates for these backends
            for be in backends:
                tpl = template_queryset.filter(
                    backend=be.ID, notification=self, is_active=True).first()
                if tpl is not None:
                    return be, tpl
            return None

        # per-protocol message cache
        cache = {}
        for contact in contacts:
            params = generic_params.copy()
            params['contact'] = contact
            proto = contact.protocol
            if proto not in cache:
                cache[proto] = _get_backend_message(proto)
            if cache[proto] is not None:
                backend, template = cache[proto]
                message = backend.build_message(template, params)
                # We're catching all exceptions here because some people
                # are bad people and can't subclass properly
                try:
                    backend.send_message(contact, message)
                except Exception as e:
                    FailedMessage.objects.create(
                        backend=backend.ID,
                        name=contact.name,
                        address=contact.address,
                        message=str(message),
                        error=str(e),
                    )


class Template(models.Model):

    class Meta:
        verbose_name = _('template')

    notification = models.ForeignKey(
        to=Notification, on_delete=models.PROTECT,
        verbose_name=_('notification'))
    backend = models.CharField(max_length=100)
    content = models.TextField()
    target = models.CharField(
        max_length=103, default='re',
        help_text=_('Who this message actually gets sent to.'))
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    def render(self, parameters: dict, autoescape=True):
        content = cast(str, self.content)
        template = templates.from_string(content)
        context = Context(parameters, autoescape=autoescape)
        return template.render(context)


class SiteContactManager(models.Manager, AbstractContactable):
    use_in_migrations = True

    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[Contact]:
        for pref in SiteContactPreference.objects.filter(
                notification=notification, is_active=True):
            sc = pref.site_contact
            yield Contact(sc.name, sc.protocol, sc.address)


# can't make this subclass AbstractContact or fields become unset-able
class SiteContact(models.Model):

    class Meta:
        verbose_name = _('site contact')
        unique_together = (('address', 'protocol'),)

    name = models.CharField(_('name'), blank=True, max_length=500)
    protocol = models.CharField(_('protocol'), max_length=100)
    address = models.CharField(_('address'), max_length=500)

    objects = SiteContactManager()

    def __str__(self):
        return self.name


class SiteContactPreference(models.Model):

    site_contact = models.ForeignKey(SiteContact, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('is active'))

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
        return '{}:{} @ {}'.format(self.backend.PROTOCOL,
                                   self.address, self.created_at)


def _init_targets():
    """
    Intialize channel settings
    """
    if not __ALL_TARGETS__:
        __ALL_TARGETS__['si'] = _('Site Contacts')
        for key, (re_name, se_name) in settings.CHANNELS.items():
            if key == '':
                __ALL_TARGETS__['re'] = re_name
                __ALL_TARGETS__['se'] = se_name
            else:
                __ALL_TARGETS__['re:' + key] = re_name
                __ALL_TARGETS__['se:' + key] = se_name


def get_targets():
    _init_targets()
    return __ALL_TARGETS__


def get_target_choices():
    _init_targets()
    return __ALL_TARGETS__.items()
