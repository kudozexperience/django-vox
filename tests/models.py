import aspy
import rules
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import signing
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import crypto
from django.utils.translation import ugettext_lazy as _

from django_vox.base import Contact, full_iri
from django_vox.models import (VoxAttach, VoxAttachments, VoxModel,
                               VoxNotification, VoxNotifications)
from django_vox.registry import actors, channels


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


class User(VoxModel, AbstractBaseUser, PermissionsMixin):

    class VoxMeta:
        attachments = VoxAttachments(
            vcard=VoxAttach(
                attr='make_vcard', mime_string='text/vcard',
                label=_('Contact Info')),
        )

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

    def get_contacts_for_notification(self, _notification):
        yield Contact(self.name, 'email', self.email)
        yield Contact(self.name, 'activity', self.get_actor_address())

    def __activity__(self):
        return aspy.Person(
            id=self.get_actor_address(),
            name=self.name)

    def get_absolute_url(self):
        return reverse('tests:user', args=[str(self.id)])

    def make_vcard(self) -> str:
        """
        Returns the text content for a RFC 2426 vCard
        """
        params = {}
        for field in ('name', 'email'):
            params[field] = getattr(self, field).replace(
                ':', '\\:').replace(';', '\\;')

        return "BEGIN:VCARD\n" \
               "VERSION:3.0\n" \
               "FN:{name}\n" \
               "EMAIL;TYPE=internet:{email}\n" \
               "END:VCARD".format(**params)


class Article(VoxModel):

    class VoxMeta:
        # we're going to use auto generated activity entries here
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification that a new article was created.'),
                actor_type='tests.user')

        )

    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='+')
    title = models.CharField(_('title'), max_length=254)
    content = models.TextField(_('content'))

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification('create', actor=self.author)

    def get_absolute_url(self):
        return reverse('tests:article', args=[str(self.id)])

    def get_subscribers(self):
        return Subscriber.objects.filter(
            Q(author=self.author) | Q(author=None))

    def get_authors(self):
        yield self.author


class Subscriber(VoxModel):
    """
    A subscriber to blog articles.

    If the author field is set, only articles from those authors
    are subscribed to; otherwise they all are.
    """

    class Meta:
        unique_together = (('author', 'email',),)

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification from subscriber that a new subscriber '
                  'was created. Intended for site admins'),
                activity_type=aspy.Create),
        )

    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_('author'),)
    name = models.CharField(_('name'), max_length=254)
    email = models.EmailField(_('email'), max_length=254, unique=True)
    secret = models.CharField(
        _('secret'), max_length=32, default='', blank=True,
        help_text=_('Used for resetting passwords'))

    def __str__(self):
        return '{} <{}>'.format(self.name, self.email)

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification('create')

    @classmethod
    def load_from_token(cls, token):
        signer = signing.Signer()
        try:
            unsigned = signer.unsign(token)
        except signing.BadSignature:
            raise ValueError("Bad Signature")

        parts = unsigned.split(' | ')
        if len(parts) < 2:
            raise ValueError("Missing secret or key")
        secret = parts[0]
        email = parts[1]
        user = cls.objects.get(email=email)
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
        parts = (self.secret, self.email)
        return signer.sign(' | '.join(parts))

    def get_contacts_for_notification(self, _notification):
        yield Contact(self.name, 'email', self.email)
        yield Contact(self.name, 'activity', self.get_actor_address())

    def __activity__(self):
        return aspy.Person(
            name=self.name, id=full_iri(self.get_absolute_url()))

    def get_absolute_url(self):
        return reverse('tests:subscriber', args=[str(self.id)])


class Comment(VoxModel):

    class VoxMeta:
        notifications = VoxNotifications(
            create=VoxNotification(
                _('Notification that a comment was posted.'),
                actor_type='tests.subscriber')
        )

    content = models.TextField(_('content'))
    poster = models.ForeignKey(to=Subscriber, on_delete=models.CASCADE)
    article = models.ForeignKey(to=Article, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification('create', actor=self.poster)

    def get_posters(self):
        yield self.poster

    def get_article_authors(self):
        yield self.article.author

    def get_absolute_url(self):
        frag = '#comment-{}'.format(self.id)
        return reverse('tests:article', args=[str(self.article.id)]) + frag

    def __activity__(self):
        # we're being hacky here to test out the automatic
        # id stuff
        obj = super().__activity__()
        return aspy.Note(
            id=obj['id'],
            name='Note',
            content=self.content)


channels[User].add_self()
channels[Article].add('sub', _('Subscribers'),
                      Subscriber, Article.get_subscribers)
channels[Article].add('author', _('Author'), User, Article.get_authors)
channels[Subscriber].add_self()
channels[Comment].add('poster', _('Poster'), Subscriber, Comment.get_posters)
channels[Comment].add('author', _('Article author'),
                      User, Comment.get_article_authors)

actors[User].set_regex(r'^~(?P<id>[0-9]+)/$')
actors[Subscriber].set_regex(r'^\.(?P<id>[0-9]+)/$')


# set up permissions for accessing user inboxes
# note that this only works for the user inboxes
# the subscriber ones are unreachable
# NOTE: these shenanigans are actually unnecessary,
# you could achieve this by removing DJANGO_VOX_VIEW_OWN_INBOX = False
# in the settings, is is just here to test the feature
@rules.predicate
def inbox_owner(user, inbox_actor):
    return user == inbox_actor


rules.add_perm('django_vox.view_inbox', inbox_owner)
