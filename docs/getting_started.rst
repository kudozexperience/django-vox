Getting Started
===============

Once you've gone through the :doc:`installation <installation>`
and configured whatever :doc:`backends <backends>` you which to support,
you're ready to start adding notifications into your model code. In
addition to the tutorial here, there is also a :doc:`demo <demo>` that
comes with this package.

Setting up the Models
---------------------

There's basically two parts to setting up the models. First, you have
to add notifications to the models that you want notifications about;
and second, you have to add implement the ``AbstractContactNetwork``
and ``AbstractContactable`` interfaces for whatever you want to
send to notifications too/from. If you only
ever want to send the notifications to the site contacts, then there's
nothing to do for step two, but that's not very fun, is it.

Adding Model Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~

Notifications in django courier are centered around models. This is
important, because it makes it possible to predictably know what
parameters will be available in the notification templates, and
provides a measure of sanity to whoever is editing them.

Any given notification can be sent to one of three possible targets:
the sender, the recipient, and the site contacts. Sometimes it doesn't
make sense for a notification to have a sender or a recipient, so
notifications can specify the positional parameters ``uses_sender``
and ``uses_recipient``. These default to ``True`` but you can set them
if a sender or a recipient doesn't make any sense given context.

To add notifications to a model, change the parent class from
``django.db.models.Model`` to ``django_courier.models.CourierModel``.
Also, add ``CourierMeta`` inner class (much like django's ``Meta``)
which contains one attribute, a tuple named ``notifications``. Each
item in the tuple should be a ``django_courier.models.CourierParam``
instance. The result might look something like::

  class User(CourierModel):

      class CourierMeta:
          notifications = (
              CourierParam(
                  'created',
                  'Notification to a user that they created an account',
                  use_sender=False),
          )

      ...

      def save(self, *args, **kwargs):
          new = self.id is None
          super().save(*args, **kwargs)
          if new:
              self.issue_notification(recipient=self)

  ...

  class PurchaseOrder(CourierModel):

      class CourierMeta:
          notifications = (
              CourierParam(
                  'received', 'Notification from shop_manager to purchaser '
                              'that an order was received.'),
              CourierParam(
                  'on_hold',  'Notification shop manager to purchaser '
                              'that an order is on hold.'),
          )

      def save(self, *args, **kwargs):
          new = self.id is None
          if not new:
              old = PurchaseOrder.objects.get(pk=self.pk)
          super().save(*args, **kwargs)
          if new:
              self.issue_notification('received', recipient=self.purchaser,
                                      sender=self.shop.manager)
          if not new and not old.on_hold and self.on_hold:
              self.issue_notification('on_hold', recipient=self.purchaser,
                                      sender=self.shop.manager)


Once you've finished adding these, you'll need to regenerate the
notifications table using the ``make_notifications`` management command::

    python3 manage.py make_notifications


Adding Contact Info
~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we have to implement the ``django_courier.models.AbstractContactNetwork``
interface for all the senders and recipients of our notifications. This
means implementing the ``get_contacts_for_notification(notification)`` method.
This method takes a notification, and returns all of the contacts that the
object has enabled for that notification. The idea behind this method is that
it allows you to implement your own notification preferences on a per-contact
basis.

For now, we're just going to make an implementation that assumes every user
will get email notifications for all notifications. We can alter the user
class to look like this::

  from django_courier.models import ContactNetwork, Contact

  class User(CourierModel, ContactNetwork):
      ...
      email = models.EmailField(max_length=254, unique=True)

      def get_contacts_for_notification(notification):
          return Contact(self.name, 'email', self.email)


.. note:: There's a lot more going on here than meets the eye, but this
   example should be enough to get you started.

And there you have it. Now, in order for this to do anything useful,
you'll need to add some appropriate :doc:`templates <templates>`.
In this case, you'll want an email template for the recipient of the
"user created" notification, and possibly a template for a site contact
too.
