==================
Settings Reference
==================

Backend-specific
================

Details about the following settings can be found in the documentation on
:doc:`backends`. They are listed here for completion.

* ``DJANGO_VOX_BACKENDS``
* ``DJANGO_VOX_TWILIO_ACCOUNT_SID``
* ``DJANGO_VOX_TWILIO_AUTH_TOKEN``
* ``DJANGO_VOX_TWILIO_FROM_NUMBER``
* ``DJANGO_VOX_TWITTER_CONSUMER_KEY``
* ``DJANGO_VOX_TWITTER_CONSUMER_SECRET``
* ``DJANGO_VOX_TWITTER_TOKEN_KEY``
* ``DJANGO_VOX_TWITTER_TOKEN_SECRET``
* ``DJANGO_VOX_XMPP_JID``
* ``DJANGO_VOX_XMPP_PASSWORD``
* ``DJANGO_VOX_POSTMARK_TOKEN``


General
=======

``DJANGO_VOX_THROW_EXCEPTIONS``
    If True, exceptions that happen during notification sending won’t be
    caught, and will bubble up. If False, exceptions are caught and
    a warning is issued instead. In either case, the failed messages and
    errors will get stored in Failed Messages. Also, this does not apply
    to the error raised by the ``required`` parameter, and it does not
    apply to messages that are being manually sent in the admin site.
``DJANGO_VOX_ISSUE_METHOD``
    This allows you to override the method that issues notifications.
    The primary use case for this is to use some sort of asynchronous job
    framework. If you install django-backgroundtasks_ and set this to
    ``"django_vox.extra.background_tasks.issue"``, it will use route
    the issuing through a background task.

.. note:: If you use django-backgroundtasks, you need to make sure you set
          it up properly and have a worker process to actually run the tasks.
          it's also probably a good idea to set ``DJANGO_VOX_THROW_EXCEPTIONS``
          to False if you use this.

Markdown
========

``DJANGO_VOX_MARKDOWN_EXTRAS``
    Add extra non-standard features to the markdown.
``DJANGO_VOX_MARKDOWN_LINK_PATTERNS``
    This pattern controls what test is auto-linked in markdown
    documents


Activity Streams
================

``DJANGO_VOX_INBOX_LIMIT``
    The maximum number of activity entries that will be shown in an actor’s
    inbox. Defaults to 500.
``DJANGO_VOX_ACTIVITY_REGEX``
    The URI regex for an activity object.

.. _django-backgroundtasks: https://pypi.org/project/django-background-tasks/

