=========================
 Registrations in Detail
=========================


.. note:: This documentation assumes that you’ve read the
          :doc:`getting_started` page.

Notifications
=============

Specifying Actors and Targets
-----------------------------

Notifications can have actors and targets. If you think of a notification as
representing a specific action, an actor is whatever caused the action, and
the target is whatever the action was done on. So for example, if have CMS
application, and you might have a notification for page editing, the actor
for the notification could be the user who edited the page, and the target
might be the page that was edited. Finally, let’s say you’re using Django’s
built-in users. You might end up with code like this


.. code-block:: python

   # models for myapp
   class Page(models.Model):
       content = models.TextField()

   class PageRegistration(Registration):

       edited = Notification(
           _("Notification that the page was edited"),
           actor_type="auth.user",
           target_type="myapp.page",
       )
   # Note: We're skipping the actual registration details here
   # Let's say you have this view elsewhere to update a page

   def update_page(request, page):
       # do some authentication
       form = PageForm(request.POST, instance=page)
       if form.is_valid():
           form.save()
           PageRegistration.edited.issue(page, actor=request.user, target=page)

Note that now ``actor`` and ``target`` are specified when issuing the
notification. These arguments are used if and only if there ``actor_type`` and
``target_type`` parameters set on the notification. Also note that these must
be specified as keyword arguments (to reduce confusion).

In this case, we’ve triggered the notification in a view instead of in
the model itself. That’s a totally valid way of doing it, but it means you
have to manually ensure the notification is triggered, and it won’t get
triggered in the admin unless you write your own ModelAdmin that does it.

Required Notifications
----------------------

Normally, if a notification is issued, but either 1) no relevant notification
templates are set up, 2) the channels are mis-configured, or 3) the contact
methods aren’t returning any results, nothing happens. In the case of 1 & 3,
this is generally the desired behavior, and it doesn’t mean there’s anything
wrong with what’s going in. It’s to be expected that sometimes the programmers
will set up a notification in the code that either isn’t actually used yet,
or is only used some of the time.

Some messages though, really should get sent all the time, and you may not
want such a failure to pass silently. If this is the case, you can pass
``required=True`` when you declare your notification. Required notifications
will raise a ``RuntimeError`` exception if the notification was issued and no
messages were actually sent.


Attachments
===========

.. note:: Attachments are currently only supported by the email backends

Similar to how notifications are defined, you can also define attachments when
making a registration class.


.. code-block:: python

   import pdfkit
   from django_vox.registry import Attachment, Registration

   class Page(models.Model):
       html_content = models.TextField()

   class PageRegistration(Registration):

       pdf = Attachment(
           # attr is an instance method, or a callable on either
           # the model itself, or the registration class.
           # If it's a callable, it takes one argument(the model instance)
           attr="as_pdf",
           # you can also you mime_attr if you need a dynamic mime type
           mime_string="application/pdf",
           # defaults to "pdf" in this case, if left blank
           label=_("PDF Copy")
       )

       @staticmethod
       def as_pdf(instance):
           """Generate PDF from page contents"""
           return pdfkit.from_string(instance.html_content, False)


The above example will let you attach a PDF copy of the page to any
page notifications. Note that the actual assignment of attachments happens
in the admin when you make notification templates, adding this just provides
the option there.

Channels
========

As you saw before on the :doc:`getting_started` page, you typically want to
specify channels on an model that either has notifications, or is used as an
actor or a target for notifications. Channels are specified in the
``get_channels`` method which returns a Mapping of string (the channel key) →
a ``django_vox.registry.Channel`` object. There’s current 3 ways to make
``Channel`` objects.

1. ``Channel.self(self)``: this means you can send notifications directly to
   the model itself.
2. ``Channel.field(Model.field)``: You can use this if “Model.field” is a
   ForeignKey, or a ManyToManyField.
3. ``Channel(label, model class, function)``: You can also create your channel
   manually. In this case, label is a string, function is a callable that
   takes one argument (a model instance of the model that this registry is for)
   and returns an iterable of the “model class” objects.

.. code-block:: python

   from django.utils import timezone
   from django.db import models
   from django_vox.registry import Channel, Registration, provides_contacts

   def youth_members(org):
       # 18 years ago
        adult_birthday = timezone.now().replace(
            year=timezone.now().year - 18)
       return org.members.filter(birthday__gte=adult_birthday)

   class Organisation(models.Model):
       org_email = models.EmailField()
       # note: I'm omitting the User class and its registration
       members = models.ManyToManyField(to=User)

       @provides_contacts("email")
       def email_contact(self, instance, notification):
           yield instance.org_email

   class OrganisationRegistration(Registration):

       def get_channels(self):
           return {
               "": Channel.self(self),
               "all": Channel.field(Organization.members),
               "youth": Channel.self(_("Youth"), User, youth_members),
           }

.. note:: The channel keys should be unique strings. They don’t need to be
          long and fancy, and won’t be visible to end users.

Builtin Registration Classes
============================

You’ve already seen the ``Registration`` class already. There’s another
built-in registration class called ``SignalRegistration``. It uses
Django’s built-in model signals and provides three notifications (created,
updated, and deleted) that automatically work. You can use this registration
class directly, but if you want to contact anything besides site contacts,
you’ll want to subclass it and add ``get_channels`` and maybe contact methods.


Registration Inheritance
========================

You can subclass registration classes, just like normal Python classes.
There’s a few things to be aware of.

1. You can only have one contact method for a given protocol. If a parent
   class has a method decorated with ``@provides_contacts("email")`` and
   the child class does too, the child class’s method will be used.
2. The same applies to notification code names. Unless you manually specify
   A notification code name, however, its always the same as attribute name,
   so this is a moot point in practice.


Site Contacts
=============

Site contacts are a special kind of contact that come build-in. You can
set them up in the Django admin site. Site contacts are global to the site,
but you can enable or disable them on a per-notification basis.

...
