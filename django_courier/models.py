from typing import List, TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from . import templates
from .backends import get_backends_from_settings


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
                           recipient: 'IContactableN' = None, sender=None):
        ct = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(
            codename=codename, content_type=ct)
        notification.issue(self, recipient, sender)


class IContact:

    @property
    def address(self) -> str:
        raise NotImplementedError()

    @property
    def protocol(self) -> str:
        raise NotImplementedError()


IContactN = TypeVar('IContactN', IContact, None)


class IContactable:

    def get_contacts_for_notification(
            self, notification: 'Notification') -> List[IContact]:
        raise NotImplementedError()


IContactableN = TypeVar('IContactableN', IContactable, None)


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
        ContentType,
        models.CASCADE,
        verbose_name=_('content type'),
    )
    description = models.TextField(_('description'))
    use_sender = models.BooleanField(_('use sender'))
    use_recipient = models.BooleanField(_('use recipient'))

    objects = NotificationManager()

    def __str__(self):
        return "{} | {} | {}".format(
            self.content_type.app_label, self.content_type, self.codename)

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()

    natural_key.dependencies = ['contenttypes.contenttype']

    def issue(self, content, recipient: IContactableN=None, sender=None):
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
            'subject': content,
            'content': content,
        }
        if self.use_recipient and (recipient is not None):
            parameters['recipient'] = recipient
        elif self.use_recipient:
            raise RuntimeError(
                'Model specified "use_recipient" for notification but '
                'recipient missing on issue_notification ')
        elif recipient is not None:
            raise RuntimeError('Recipient added to issue_notification, '
                               'but is not specified in CourierMeta')

        if self.use_sender and (sender is not None):
            parameters['sender'] = sender
        elif self.use_sender:
            raise RuntimeError(
                'Model specified "use_sender" for notification but sender '
                'missing on issue_notification ')
        elif sender is not None:
            raise RuntimeError('Sender added to issue_notification, but is '
                               'not specified in CourierMeta')

        contact_map = {
            're': recipient,
            'si': SiteContact,
            'se': sender,
        }
        for key, value in contact_map.items():
            if value is not None:
                self.send_messages(
                    value.get_contacts_for_notification(self),
                    parameters,
                    Template.objects.filter(target=key))

    def send_messages(self, contacts, parameters, template_queryset):
        def _get_backend_message(protocol):
            backends = get_backends_from_settings(protocol)
            # now get all the templates for these backends
            for be in backends:
                template = template_queryset.filter(
                    backend=be.ID, notification=self, is_active=True).first()
                if template is not None:
                    return be, be.build_message(template, parameters)
            return None

        # per-protocol message cache
        cache = {}
        for contact in contacts:
            protocol = contact.protocol
            if protocol not in cache:
                cache[protocol] = _get_backend_message(protocol)
            if cache[protocol] is not None:
                backend, message = cache[protocol]
                # We're catching all exceptions here because some people
                # are bad people and can't subclass properly
                try:
                    backend.send_message(contact, message)
                except Exception as e:
                    FailedMessage.objects.create(
                        backend=backend.ID,
                        protocol=protocol,
                        address=contact.address,
                        message=str(message),
                        error=str(e),
                    )


class Template(models.Model):

    TARGET_CHOICES = (
        ('re', _('Recipient')),
        ('si', _('Site Contacts')),
        ('se', _('Sender')),
    )

    class Meta:
        default_permissions = ()
        verbose_name = _('template')

    notification = models.ForeignKey(
        Notification, verbose_name=_('notification'))
    backend = models.CharField(max_length=100)
    content = models.TextField()
    target = models.CharField(
        choices=TARGET_CHOICES, max_length=2, default='re',
        help_text=_('Who this message actually gets sent to.'))
    is_active = models.BooleanField(default=True)

    def render(self, parameters: dict, autoescape=True):
        template = templates.from_string(self.content)
        context = Context(parameters, autoescape=autoescape)
        return template.template.render(context)


class SiteContact(models.Model):

    class Meta:
        default_permissions = ()
        verbose_name = _('site contact')
        unique_together = (('address', 'protocol'),)

    address = models.CharField(_('address'), max_length=500)
    protocol = models.CharField(_('protocol'), max_length=100)

    @classmethod
    def get_contacts_for_notification(
            cls, notification: 'Notification') -> List[IContact]:
        queryset = SiteContactPreference.objects
        for pref in queryset.filter(notification=notification,
                                    is_active=True):
            yield pref.site_contact


class SiteContactPreference(models.Model):

    site_contact = models.ForeignKey(SiteContact, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_active = models.BooleanField(_('is active'))


class FailedMessage(models.Model):

    class Meta:
        default_permissions = ()
        verbose_name = _('failed message')

    backend = models.CharField(_('backend'), max_length=100)
    address = models.CharField(_('address'), max_length=500)
    protocol = models.CharField(_('protocol'), max_length=100)
    message = models.TextField(_('message'))
    error = models.TextField(_('error'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
