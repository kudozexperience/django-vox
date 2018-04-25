======================
Notification Templates
======================

Notification templates use django's build-in `templating`_ system. This
gives us more than enough power to craft the kind of message we want,
without making things too onerous.


Example
=======

The way a template looks shouldn't be too foreign to you if you're already
used to django; but just in case you're wondering, here's an example::

    <p>Hi {{ contact.name }},</p>

    <p>{{ content.poster.name }} has posted a comment on your blog titled
    {{ content.article.title }}.</p>

Note that the exact variables available will depend on which model the
notification is attached to.


Variables
=========

Several variables are provided to you in the template context.

``content``
    This refers to whatever model the notification is attached to. It is
    visible as the content-type field of the notification when you're
    editing it in the admin. Most of the time, you're probably going to
    be wanting to use this.
``contact``
    The ``Contact`` object that the message is being sent to. This object
    has 3 attributes: ``name``, ``protocol``, and ``address``.
``recipient``
    The type of this depends on which channel is selected as the recipient
    of a notification, and what kind of objects that channel returns. In
    practice, it will probably be some sort of user/user-profile object.
    When site contacts are the recipient, the value is a ``SiteContact``
    object.
``source``
    This is only available if source_model is specified for the notification.
    It refers to whoever or whatever is causing action associated with the
    notification.
``target``
    This is only available if target_model is specified for the notification.
    It refers to whoever or whatever the action associated with the
    notification is affecting.

Most of the time, it's recommended to just try and use a field on the
``content`` variable instead of ``target`` or ``source``. Sometimes, though,
this is just not possible, and you want to be able to differentiate between
the two at runtime, so that's why they exist.


Miscellaneous Notes
===================

Escaping
--------

Django's template engine has been primarily designed for outputting HTML.
The only place in which this really matters is when it comes to excaping
content. Plain text and HTML content work fine, however, with other formats
like Markdown we need to wrap all the template variables with a custom
variable escaping object that escapes everything on the fly. This has a few
consequences.

1. Most variables will be wrapped in this class. While the class mostly
   mimics the behavior of the underlying object, any template filter using
   ``isinstance`` will fail.
2. In order to maintain compatibility with template filters, we don't try
   to escape any of the basic numeric or date/time objects. For the most
   part this is okay, but it is theoretically possible to end up with a
   weird result.
3. The result of template filters is typically not escaped correctly.


Subjects
--------

Templates have a subject field which is sometimes used, depending on
the backend. Any backend which supports a subject, has the attribute
``USE_SUBJECT`` set to ``True``. Setting a subject on a template
who's backend doesn't use it has no effect.

.. _templating: https://docs.djangoproject.com/en/dev/ref/templates/language/
