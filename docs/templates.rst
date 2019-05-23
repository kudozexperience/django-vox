======================
Notification Templates
======================

Notification templates use django’s build-in `templating`_ system. This
gives us more than enough power to craft the kind of message we want,
without making things too onerous. Here, we go over the various fields
on a template object, and what they do.

Fields
=======

Backend
    This sets the :doc:`backend <backends>` that the template will use.
Recipients
    Here, you can select one or multiple kinds of recipients. If none are
    selected, the template won’t be used.
Subject
    You can use template variables here but be careful not to make it
    too long. [1]_
Content
    Here’s where the body of your message goes. You can use template variables
    here and there is a toolbar at the top of the text books that has a few
    tools for convenience. Of particular note is the check mark button (✓) that
    shows a preview. Use this to check your template.
Attachments
    You can add zero-multiple attachments here. What’s available here depends
    on what’s set up in the code [2]_
From address
    Normally optional since backends have a way to specify a site-wide default
    from address if they need one at all. You can use template variables here.
    [3]_
Bulk
    When this is on, only one message will be sent per template to all
    recipients and the ``recipients`` parameter will not be available. When
    it is turned off, a separate message will be made for each recipient, and
    you can use the ``recipients`` parameter.
Enabled
    Turning this off will case the template to be ignored.


Example Content
===============

The way a template looks shouldn’t be too foreign to you if you’re already
used to django; but just in case you’re wondering, here’s an example.

.. code-block:: html

   <p>Hi {{ recipient.name }},</p>

   <p>{{ object.poster.name }} has posted a comment on your blog titled
   {{ object.article.title }}.</p>

Note that the exact variables available will depend on which model the
notification is attached to. This example assumes ``bulk`` is turned off.


Variables
=========

Several variables are provided to you in the template context.

``object``
    This refers to whatever model the notification is attached to. It is
    visible as the content-type field of the notification when you’re
    editing it in the admin. Most of the time, you’re probably going to
    be wanting to use this.
``actor``
    This is only available if ``actor_type`` is specified for the notification.
    It refers to whoever or whatever is causing action associated with the
    notification.
``target``
    This is only available if ``target_model`` is specified for the notification.
    It refers to whoever or whatever the action associated with the
    notification is affecting.
``recipient``
    The type of this depends on which channel is selected as the recipient
    of a notification, and what kind of objects that channel returns. In
    practice, it will probably be some sort of user/user-profile object.
    When site contacts are the recipient, the value is a ``SiteContact``
    object.

Most of the time, it’s recommended to just try and use a field on the
``object`` variable instead of ``target`` or ``actor``. Sometimes, though,
this is just not possible, and you want to be able to differentiate between
the two at runtime, so that’s why they exist.


Miscellaneous Notes
===================

Escaping and Markdown
---------------------

Django’s template engine has been primarily designed for outputting HTML.
The only place in which this really matters is when it comes to escaping
content. Plain text and HTML content work fine, however, with other formats
like Markdown we need to wrap all the template variables with a custom
variable escaping object that escapes everything on the fly. This has a few
consequences.

1. Most variables will be wrapped in this class. While the class mostly
   mimics the behavior of the underlying object, any template filter using
   ``isinstance`` will fail.
2. In order to maintain compatibility with template filters, we don’t try
   to escape any of the basic numeric or date/time objects. For the most
   part this is okay, but it is theoretically possible to end up with a
   weird result.
3. The result of template filters is typically not escaped correctly.


.. _templating: https://docs.djangoproject.com/en/dev/ref/templates/language/

.. [1] The subject field only shows if the backend supports it, i.e. it has
        ``USE_SUBJECT`` set to ``True``.
.. [2] The attachments field only shows if the backend supports it, i.e. it
        has ``USE_ATTACHMENTS`` set to ``True``.
.. [3] The from address field only shows if the backend supports it, i.e. it
        has ``USE_FROM_SUBJECT`` set to ``True``.
