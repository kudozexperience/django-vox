===============
Getting Started
===============

Installation
============

Getting the code
----------------

The recommended way to install django-vox is via pip_ (on Windows,
replace ``pip3`` with ``pip``) ::

    $ pip3 install django-vox[markdown,twilio,html]

.. _pip: https://pip.pypa.io/


Configuring Django
------------------

Add ``'django_vox'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        'django_vox',
    ]

Additionally, you may want to configure certain :doc:`backends <backends>`
depending on exactly what sort of other notifications you want.


The Demo
========

While you're welcome to use the setup instructions here, it may be easier
to just try out the :doc:`demo <demo>` that comes with this package. The
demo doesn't cover all the use cases (yet) but it does cover most of the
standard stuff.


Setting up the Models
=====================

There's basically two parts to setting up the models. First, you have to
add notifications to the models that you want notifications about. Second,
you have to add `channels` to those notifications to specify where they
can be sent. Finally, you need to implement the ``AbstractContactable``
interfaces for whatever your channels return so that we now how to contact
them.

If you only ever want to send notifications to the site contacts, you can
skip step 2 and 3, but that's not very fun, is it.

Adding Model Notifications
--------------------------

Notifications in django vox are centered around models. This is
important, because it makes it possible to predictably know what
parameters will be available in the notification templates, and
provides a measure of sanity to whoever is editing them.

To add notifications to a model, change the parent class from
``django.db.models.Model`` to ``django_vox.models.VoxModel``.
Also, add ``VoxMeta`` inner class (much like django's ``Meta``)
which contains one attribute, a tuple named ``notifications``. Each
item in the tuple should be a ``django_vox.models.VoxParam``
instance. The result might look something like::

  class User(VoxModel):

      class VoxMeta:
          notifications = (
              VoxParam(
                  'created',
                  'Notification to that a user created an account'),
          )

      ...

      def save(self, *args, **kwargs):
          new = self.id is None
          super().save(*args, **kwargs)
          if new:
              self.issue_notification('created')

  ...

  class PurchaseOrder(VoxModel):

      class VoxMeta:
          notifications = (
              VoxParam(
                  'received', 'Notification that an order was received.'),
              VoxParam(
                  'on_hold',  'Notification that an order is on hold.'),
          )

      def save(self, *args, **kwargs):
          new = self.id is None
          if not new:
              old = PurchaseOrder.objects.get(pk=self.pk)
          super().save(*args, **kwargs)
          if new:
              self.issue_notification('received')
          if not new and not old.on_hold and self.on_hold:
              self.issue_notification('on_hold')


Once you've finished adding these, you'll need to regenerate the
notifications table using the ``make_notifications`` management command::

    python3 manage.py make_notifications


Adding Channels
---------------

Channels are what allow you to select different recipients. The site contacts
channel is available by default, but if you want any other channels, you have
to create them yourself using the channel registry at
``django_vox.registry.channels``. You can add new channels using either the
``add`` or ``add_self`` method takes four arguments:

``key``
   A slug that identifies the channel. Should be unique per model.
``name``
   A name that shows up in the admin. Optional, defaults to various automatic
   values.
``recipient_type``
   Model class of the objects returned by the function. Optional, defaults
   to the VoxModel subclass (i.e. ``Foo`` in ``Foo.add_channel``).
``func``
   A function or method that returns the instances of ``recipient_type``.
   The function is called with a single argument which is the VoxModel
   instance that will eventually use it (i.e. the ``content`` object).
   Optional, defaults to ``lambda x: x``


An example of channels given the above code might look like this::

    class PurchaseOrder(VoxModel):
        ...
        def get_purchasers(self):
            yield self.purchaser

        def get_managers(self):
            yield self.shop.manager

    ...

    from django_vox.registry import channels
    channels[User].add_self()
    channels[PurchaseOrder].add('purchaser', _('Purchaser'), User,
        PurchaseOrder.get_purchasers)
    channels[PurchaseOrder].add('manager', _('Manager'), User,
        PurchaseOrder.get_managers)


Adding Contact Info
-------------------

Now we have to implement the ``get_contacts_for_notification(notification)``
method for all the things that are return in channels. In our above
example, that's just the ``User`` model. This method takes a notification,
and returns all of the contacts that the object has enabled for that
notification. The idea behind this method is that it allows you to implement
your own notification settings on a per-contact basis.

For now, we're just going to make an implementation that assumes every user
will get email notifications for all notifications. We can alter the user
class to look like this::

  from django_vox.models import VoxModel
  from django_vox.base import Contact

  class User(VoxModel):
      ...
      email = models.EmailField(max_length=254, unique=True)

      def get_contacts_for_notification(notification):
          return Contact(self.name, 'email', self.email)


.. note:: We haven't covered sources or targets, but this example should
   be enough to get you started.

And there you have it. Now, in order for this to do anything useful,
you'll need to add some appropriate :doc:`templates <templates>`.
In this case, you'll want an email template for the "User" recipient of the
"user created" notification, and possibly a template for a site contact
too.
