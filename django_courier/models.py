# temporary file for testing purposes

import pydoc

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from typing import TypeVar, List
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.conf
import django.template
from . import templates, settings


PROTOCOLS = {
    'email',
    'sms',
    'slack',
}


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
                    raise ValueError('class CourierMeta has invalid attribute: {}'.format(key))


class CourierModelBase(models.base.ModelBase):
    """
    Metaclass for Courier extensions. Deals with notifications on CourierOptions
    """
    def __new__(mcs, name, bases, attributes):
        new = super(CourierModelBase, mcs).__new__(mcs, name, bases, attributes)
        meta = attributes.pop('CourierMeta', None)
        setattr(new, '_courier_meta', CourierOptions(meta))
        return new


class CourierModel(models.Model, metaclass=CourierModelBase):
    """
    Base class for models that implement notifications
    """

    class Meta:
        abstract = True

    def issue_notification(self, codename: str, recipient: 'IContactableN' = None, sender=None):
        ct = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(codename=codename, content_type=ct)
        notification.issue(self, recipient, sender)


class IContact:

    @property
    def address(self) -> str:
        raise NotImplemented

    @property
    def protocol(self) -> str:
        raise NotImplemented


IContactN = TypeVar('IContactN', IContact, None)


class IContactable:

    def get_contacts_for_notification(self, notification: 'Notification') -> List[IContact]:
        raise NotImplemented


IContactableN = TypeVar('IContactableN', IContactable, None)


class Contact(models.Model):

    class Meta:
        default_permissions = ()
        verbose_name = _('contact')
        unique_together = (('user', 'address', 'backend'),)

    user = models.ForeignKey(
        django.conf.settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=500)
    backend = models.CharField(max_length=100)


class NotificationBackend:

    @classmethod
    def send(cls, template: 'Template', contact: IContact, parameters: dict):
        raise NotImplementedError


class EmailBackend(NotificationBackend):

    ID = 'email'
    PROTOCOL = 'email'

    @staticmethod
    def get_backend() -> 'django.core.mail.backends.base.BaseEmailBackend':
        return django.core.mail.backends.smtp.EmailBackend()

    @classmethod
    def send(cls, template, contact, parameters):
        backend = cls.get_backend()
        email = templates.parts_from_string(template.content, parameters)
        email.from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        email.to = [contact.address]
        backend.send_messages([email])


class PostmarkTemplateBackend(EmailBackend):

    ID = 'postmark_template'

    @staticmethod
    def get_backend():
        import anymail.backends.postmark
        return anymail.backends.postmark.EmailBackend()

    @classmethod
    def send(cls, template, contact, parameters):
        from anymail.message import AnymailMessage
        backend = cls.get_backend()
        from_email = django.conf.settings.DEFAULT_FROM_EMAIL
        to_email = [contact.address]
        email = AnymailMessage('', '', from_email, to_email)
        email.template_id = template.content
        email.merge_global_data = parameters
        backend.send_messages([email])


class TwilioBackend:

    ID = 'twilio'
    PROTOCOL = 'sms'

    @classmethod
    def send(cls, template, contact, parameters):
        from twilio.rest import Client
        if not hasattr(django.conf.settings, 'TWILIO_ACCOUNT_SID'):
            raise django.conf.ImproperlyConfigured(
                'Twilio backend enabled but TWILIO_* settings missing')
        account_sid = django.conf.settings.TWILIO_ACCOUNT_SID
        auth_token = django.conf.settings.TWILIO_AUTH_TOKEN
        from_number = django.conf.settings.TWILIO_FROM_NUMBER
        client = Client(account_sid, auth_token)
        # TODO: track result
        client.messages.create(
            to=contact.address, from_=from_number, body=template.render(parameters))


class NotificationManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, codename, app_label, model):
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
    description = models.TextField()
    use_sender = models.BooleanField()
    use_recipient = models.BooleanField()

    objects = NotificationManager()

    def __str__(self):
        return "{} | {} | {}".format(
            self.content_type.app_label, self.content_type, self.codename)

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()

    natural_key.dependencies = ['contenttypes.contenttype']

    def issue(self, subject, recipient: IContactableN=None, sender=None):
        """
        To send a notification to a user, get all the user's active methods.
        Then get the backend for each method and find the relevant template to send
        (and has the said notification). Send that template with the parameters
        with the backend.

        :param subject: model object that the notification is about
        :param recipient: either a user, or None if no logical recipient
        :param sender: user who initiated the notification
        :return: None
        """
        # check
        parameters = {'subject': subject}
        if self.use_recipient and (recipient is not None):
            parameters['recipient'] = recipient
        elif self.use_recipient:
            raise RuntimeError(
                'Model specified "use_recipient" for notification but recipient missing on issue_notification ')
        elif recipient is not None:
            raise RuntimeError('Recipient added to issue_notification, but is not specified in CourierMeta')

        if self.use_sender and (sender is not None):
            parameters['sender'] = sender
        elif self.use_sender:
            raise RuntimeError(
                'Model specified "use_sender" for notification but sender missing on issue_notification ')
        elif sender is not None:
            raise RuntimeError('Sender added to issue_notification, but is not specified in CourierMeta')

        # TODO: implement site contacts
        if recipient is not None:
            contacts = recipient.get_contacts_for_notification(self)
            for contact in contacts:
                backends = get_backends_from_settings(contact.protocol)
                # now get all the templates for these backends
                for backend in backends:
                    template = Template.objects.filter(
                        backend=backend.ID, notification=self, is_active=True).first()
                    if template is not None:
                        backend.send(template, contact, parameters)
                        break


class Template(models.Model):

    class Meta:
        default_permissions = ()
        verbose_name = _('template')

    notification = models.ForeignKey(
        Notification, verbose_name=_('notification'))
    backend = models.CharField(max_length=100)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    def render(self, parameters: dict):
        template = templates.from_string(self.content)
        return template.render(parameters)


def get_backends_from_settings(protocol: str):
    for name in settings.BACKENDS:
        cls = pydoc.locate(name)
        if cls.PROTOCOL == protocol:
            yield cls
