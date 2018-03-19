from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import signing
from django.db import models
from django.utils import crypto
from django.utils.translation import ugettext_lazy as _

from django_courier.models import (CourierModel, CourierParam, IContact,
                                   IContactable)


class UserContact(IContact):

    def __init__(self, protocol: str, address: str):
        self._protocol = protocol
        self._address = address

    @property
    def address(self):
        return self._address

    @property
    def protocol(self):
        return self._protocol


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **kwargs,
        )

        if password is not None:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            name=name,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(IContactable, CourierModel, AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email'), max_length=254, unique=True)
    name = models.CharField(_('name'), max_length=254)
    is_staff = models.BooleanField(
        verbose_name=_('staff status'), default=False,
        help_text=_('Designates whether the user can '
                    'log into this admin site.'))
    is_active = models.BooleanField(
        verbose_name=_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Un-select this instead of deleting accounts.'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return '{0} <{1}>'.format(self.name, self.email)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_contacts_for_notification(self, notification):
        yield UserContact('email', self.email)


class Article(CourierModel):

    class CourierMeta:
        notifications = (
            CourierParam(
                'created', _('Notification to followers that a new article '
                             'was created.'),
            ),
        )

    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='+')
    title = models.CharField(_('title'), max_length=254)
    content = models.TextField(_('content'))

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            for follower in Follower.objects.all():
                self.issue_notification('created', sender=self.author,
                                        recipient=follower)


class Follower(CourierModel, IContactable):

    class Meta:
        unique_together = (('email',),)

    class CourierMeta:
        notifications = (
            CourierParam(
                'created', _('Notification from follower that a new follower '
                             'was created. Intended for site admins'),
                use_recipient=False,
            ),
        )

    name = models.CharField(_('name'), max_length=254)
    email = models.EmailField(_('email'), max_length=254, unique=True)
    secret = models.CharField(
        _('secret'), max_length=32, default='', blank=True,
        help_text=_('Used for resetting passwords'))

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification('created', sender=self)

    @classmethod
    def load_from_token(cls, key):
        signer = signing.Signer()
        try:
            unsigned = signer.unsign(key)
        except signing.BadSignature:
            raise ValueError("Bad Signature")

        parts = unsigned.split(' | ')
        if len(parts) < 2:
            raise ValueError("Missing secret or key")
        secret = parts[0]
        natural_key = parts[1:]
        user = cls.objects.get_by_natural_key(*natural_key)
        if user.secret != secret:
            raise LookupError("Wrong secret")
        return user

    def get_token(self):
        """Makes a verify to verify new account or reset password

        Value is a signed 'natural key' (email address)
        Reset the token by setting the secret to ''
        """
        if self.secret == '':
            self.secret = crypto.get_random_string(32)
            self.save()
        signer = signing.Signer()
        parts = (self.secret,) + self.natural_key()
        return signer.sign(' | '.join(parts))

    def get_contacts_for_notification(self, notification):
        yield UserContact('email', self.email)


class Comment(CourierModel):

    class CourierMeta:
        notifications = (
            CourierParam(
                'created', _('Notification from follower to author that a '
                             'comment was posted')),
        )

    content = models.TextField(_('content'))
    poster = models.ForeignKey(to=Follower)
    article = models.ForeignKey(to=Article)

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification('created', sender=self.poster,
                                    recipient=self.article.author)
