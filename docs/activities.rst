============
 Activities
============

The activities backend provides support for the `Activity Streams`_ (and very
slightly `ActivityPub`_) standards. Message are stored locally in the database
and are retrievable from an inbox. References to notions like actors and
inboxes refer to the ideas in that standard.

.. _Activity Streams: https://www.w3.org/TR/activitystreams-core/
.. _ActivityPub: https://www.w3.org/TR/2018/REC-activitypub-20180123/


Setting up the activities is fairly involved, and also entirely optional
unless you actually want to use the activity backend. As a result, it’s
got its own documentation. Note that this backend is somewhat experimental.
Don’t use it in production unless you’ve tested it well and know
what you’re doing.


Settings
========

Because we need to generate full URIs (including the domain) and
we need to be able to do it without an HTTP request, we need to
have a way of finding out your domain & scheme. If you're already
using ``django.contrib.sites`` and you have it set up with a
``SITE_ID`` in your settings, that’ll work. Otherwise a simpler
solution is to just set these two settings:

===============  ======================================
``SITE_DOMAIN``  Your site’s domain name
``SITE_SSL``     True if you use HTTPS, False otherwise
===============  ======================================

.. caution:: ``SITE_SSL`` should nearly always be True (the default) unless
   you’re in development testing on localhost.

Also, because this backend isn’t enabled by default, you’ll need to
alter ``DJANGO_VOX_BACKENDS`` and add
``'django_vox.backends.activity.Backend',``. You can see an example on the
:doc:`backends` page.

.. note:: Sometimes you might see a URI called an IRI. They're slightly
          different, but they're similar enough that you can probably assume
          they're the same without hastening the return of Zalgo.

Registering URIs
================

You've probably noticed the ``regex=None`` argument earlier on when
registering objects, and wondered what it was all about. Till now we've
ignored it because it’s only really used with activity stream notifications.

The regex value is used to tell us the canonical location of a given
model instance. It's sort of like using ``get_absolute_url`` except that
you can register it on models you didn't write, and we can reverse the
pattern to look up an object based on its URI.

If you're planning to use the activity streams backend, here's the deal:

* Any model that will be a recipient of notifications must have a regex value.
* Any model that will be the object, actor, or target type of notifications
  should have a regex value.

It's recommended that this URI is also a public URL that people can generally
fetch with HTTP to get details about the object, but that's not strictly
necessary.

Here's a sample in code that you might implement based on the purchase order
sample in the :doc:`getting_started` page.

.. code-block:: python

   class UserRegistration(Registration):

       @provides_contacts("activity")
       def activity_contact(self, instance, notification):
           yield self._get_object_address(instance)

       ...

   # add the URIs to the registration
   objects.add(User, UserRegistration, regex=r'^users/(?P<username>\w+)/$')
   objects.add(
       PurchaseOrder, PurchaseOrderRegistration, regex=r'^po/(?P<id>[0-9]+)/$'
   )


Customizing Activity Types
==========================

Just like we had to add a bunch of properties to the registration for the
basic features in Django Vox, there’s a few more to add to get good results for
the activity stream. These aren’t strictly necessary, but your results will
be pretty plain without them. Code samples of all of these are available in
the test site the comes with Django Vox.

First, the notification parameters take another parameter ``activity_type``.
It can be set to an ``aspy.Activity`` subclass. If it’s not set, django_vox
with either match the notification name to an activity type, or use the
default ‘Create’ type.

.. note:: This code makes use of the ``aspy`` library. It’s a dependency, so
          you should get it automatically, just ``import aspy``.

Second, the object of your activity entries defaults to the plain activity
streams “Object” with an id (based on ``get_absolute_url()`` and a name
(based on ``__str__()``). This is pretty bare-bones to say the least. You can
specify something more colorful by implementing the ``__activity__()`` method
and returning another subclass of ``aspy.Object`` with perhaps a few
properties.

Finally, there’s a few rare cases where the same model might need to give
you different objects for different kinds of notifications. If you need to
do this, you can override ``Registration.get_activity_object()``.

.. note:: If your model is registered with ``django_vox.registry.objects``,
          it’s recommended to use ``Registration.get_object_address()``
          to get the object’s ID, otherwise you can use
          ``django_vox.base.full_iri(self.get_absolute_url())``.


Accessing the Inboxes
=====================

At this point, you should be able to make up activity notifications, issue
them, and then retrieve them using ``django_vox.models.InboxItem``. However,
if you want to use our hackish ActivityPub half-implementation, there’s one/two
more steps. First we have to enable the inbox middleware. Add this to your
settings.py:

.. code-block:: python

   MIDDLEWARE = [
       ...
       'django_vox.middleware.activity_inbox_middleware',
   ]

For security reasons, you'll also need to override ``has_activity_endpoint``
in the registration for whatever model will own the inbox. Extending the
previous example, it might look like:

.. code-block:: python

   class UserRegistration(Registration):

       def has_activity_endpoint(self, instance):
           return True

There‘s still a few things that remain to be documented, like reading inbox
items, and adding the ability to perform actions on data in your models by
posting to the inbox.
