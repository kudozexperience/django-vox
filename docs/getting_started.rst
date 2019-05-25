===============
Getting Started
===============

Installation
============

Getting the code
----------------

The recommended way to install django-vox is via pip_ (on Windows,
replace ``pip3`` with ``pip``) ::

    $ pip3 install django-vox[markdown,twilio]

.. _pip: https://pip.pypa.io/


Configuring Django
------------------

Add ``"django_vox"`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        "django_vox",
    ]

Additionally, you may want to configure certain :doc:`backends <backends>`
depending on exactly what sort of other notifications you want.


The Demo
========

While you’re welcome to use the setup instructions here, it may be easier
to just try out the :doc:`demo <demo>` that comes with this package. The
demo doesn’t cover all the use cases (yet) but it does cover most of the
standard stuff.


Registering the Models
======================

The process of issuing and routing notifications in Django Vox happens in 4
steps.

1. **Notification definitions**: These definitions are registered, and
   attached to specific models.

2. **Recipients**: Any given notification can have 4 possible recipients.

   1. The model that the notification is attached to
   2. The actor of the notification (optional)
   3. The target of the notification (optional)
   4. The site contacts (these come built-in)

3. **Channels**: Additionally, each of these recipients can have zero, 1, or
   multiple “channels”. For example, a User model might have one channel for
   the user themselves, one for the user’s followers, and one for the user’s
   emergency contact.

4. **Contact**: A contact specifies the actual address that a the notifications
   are sent to. Any model specified in a channel, should also define contacts
   in its registration, otherwise that recipient won’t have any way of
   receiving the notifications.

Any model that will be either issuing notifications, or receiving them should
have a registration. It might look something like this:

.. code-block:: python

   from django.db import models
   from django_vox.registry import (Registration, Notification, Channel,
                                    Contact, objects, provides_contacts)

   class User(models.Model):

       username = models.CharField(max_length=100, unique=True, db_index=True)
       # required email, optional mobile_phone
       email = models.EmailField(blank=False)
       mobile_phone = models.CharField(blank=True, max_length=50)

       def get_full_name(self):
           ...

       ...


   class UserRegistration(Registration):


       @provides_contacts("email")
       def email_contact(self, instance, notification):
           # you can return just the address
           yield instance.email

       @provides_contacts("sms")
       def email_contact(self, instance, notification):
           if instance.mobile_phone:
               # or you can also ret a full contact object
               # if you want to manually specify the name
               yield Contact(
                   instance.get_full_name(),
                   "email",
                   instance.mobile_phone)

       def get_channels(self):
           return {"": Channel.self(self)}

   class PurchaseOrder(models.Model):

       customer = models.ForeignKey(User, on_delete=models.PROTECT)

       def save(self, *args, **kwargs):
           created = self.id is None
           if not created:
               old = PurchaseOrder.objects.get(pk=self.pk)
           else:
               old = None
           super().save(*args, **kwargs)
           objects[self.__class__].registration.post_save(
               created, old, self)


   class PurchaseOrderRegistration(Registration):

       received = Notification(
           _("Notification that order was received."))
       on_hold = Notification(
           _("Notification that order is on hold."))

       def post_save(self, created, old, new):
           if created:
               self.received.issue(new)
           if old and not old.on_hold and new.on_hold:
               self.on_hold.issue(new)

       def get_channels(self):
           return {"cust": Channel.field(PurchaseOrder.customer)}

   # the actual registration
   objects.add(User, UserRegistration, regex=None)
   objects.add(PurchaseOrder, PurchaseOrderRegistration, regex=None)

In the above example, you have a User model, which can receive emails, and
optionally an SMS message. You also have purchase orders that have two
notifications registered on them (``received`` and ``on_hold``). Whenever
the purchase order is saved, it calls ``post_save`` on the registration object,
and that fires the notifications themselves.

Once you’ve finished adding these, you’ll need to regenerate the
notifications table using the ``make_notifications`` management command::

    python3 manage.py make_notifications



And there you have it. Now, in order for this to do anything useful,
you’ll need to add some appropriate :doc:`templates <templates>`.
In this case, you’ll want an email template for the "customer" recipient of
the purchase order notifications, and possibly a template for a site contact
too.

For more details on model registration and the various options, see the
:doc:`registrations` page.


One-time Messages from the Admin
================================

The normal way to handle notifications is call ``notification.issue(instance)``
from within the code. It’s also possible to manually issue notifications
from the admin as long as a notification doesn’t have an actor/target model.
The other way of sending messages completely bypasses the ``Notification``
models and uses an Admin Action.

In order to send messages this way, you need to add the
``django_vox.admin.notify`` action to your ``ModelAdmin`` class. It might look
something like this:

.. code-block:: python

   from django.contrib import admin
   from django_vox.admin import notify

   class UserAdmin(admin.ModelAdmin):
       actions = (notify, )

   admin.site.register(YourUserModel, UserAdmin)

In order for this to work right, the model in question is treated as the
channel,  and so needs to have contacts registered for the appropriate
backend & protocol that you want to use.

.. note:: Because we don’t actually have a notification model here, a fake
          notification (``django_vox.models.OneTimeNotification``) is passed
          to the contact methods. This can be used if only want
          certain contacts to be accessible in this way.
