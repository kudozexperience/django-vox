Comparison with similar projects
================================

Django Vox is great if you:

* Have content authors who are not programmers
* Use a current versions of Django/Python
* Want to be able to send notifications by multiple protocols
* Don't need "web-scale" (tip: if you're using Django, you don't
  need "web-scale")
* You don't want to maintain a separate web service

That said here's a more in-depth comparison between Django Vox and
some specific alternatives.


* `Pinax notifications <https://pypi.python.org/pypi/pinax-notifications>`_

  - Upsides

    + Less setup
    + Comes with notification settings editor

  - Downsides

    + Templates are part of django's template system, so you can't edit
      them from the admin.
    + Template parameters must be specified whenever sending a message.
      You need to know ahead of time, what parameters the template authors
      might want down the road.
    + Notification recipients must be users
    + Only supports email
    + Doesn't support HTML email

  - Neither

    + Notification types can be created anywhere in the code, this means
      more flexibility, but potentially more confusion too.

* `django-courier <https://github.com/h3/django-courier>`_

  - Upsides:

    + Uses signals, so you don't have to specify your own notification types
    + No code required

  - Downside

    + Only supports emails
    + Doesn't support HTML email
    + The documentation is very lacking
    + Specifying addresses is convoluted
    + Maybe dead

  - Neither

    + Supports (and requires) ``django.contrib.sites``

* `universal_notifications <https://pypi.python.org/pypi/universal_notifications>`_

  - Upsides:

    + Supports many backends

  - Downsides:

    + Backends have to know about the structure of the user object
    + Notification recipients must be users
    + Email subjects are hard-coded
    + Templates aren't easily editable in the admin

* `django-herald <https://pypi.python.org/pypi/django-herald>`_

  - Upsides:

    + Supports email attachments

  - Downsides:

    + Templates are part of django's template system, so you can't edit
      them from the admin.
    + Notification subjects are stored in the code
    + Only supports emails
    + Notification recipients must be users (though its possible to work
      around this)

* `django-notifier <http://pypi.python.org/pypi/django-notifier>`_

  - Upsides:

    + Easy setup

  - Downsides:

    + Only supports emails by default
    + Doesn't support HTML email
    + Notification recipients must be users
    + Custom backends must make assumptions about structure of user object

* `django-notifications <http://pypi.python.org/pypi/django-notifications>`_

  - Upsides:

    + Supports more backends
    + Supports filters

  - Downsides:

    + Old, and depends on an long-out-of-date version of django
    + Notification recipients must be users

* `django-heythere <http://pypi.python.org/pypi/django-heythere>`_

  - Upsides:

    + Provides in-app notifications

  - Downsides:

    + Notification types and templates are stored in ``settings.py``
    + Only supports emails
    + Doesn't support HTML email

* `django-push-notifications <https://pypi.python.org/pypi/django-push-notifications>`_

  - Upsides:

    + Supports push notifications

  - Downsides:

    + Only supports push notifications
    + No templates
    + Notification recipients must be users

* `django-sitemessage <https://pypi.python.org/pypi/django-sitemessage>`_

  - Upsides:

    + Supports many backends

  - Downsides:

    + Configuration is done in code
    + Not possible to specify different messages for different backends

* `django-gcm <https://pypi.python.org/pypi/django-gcm/>`_

  - Downsides:

    + Like django-push-notifications but worse

* `django-webpush <https://pypi.python.org/pypi/django-webpush>`_

  - Downsides:

    + Like django-push-notifications but only supports web push

* `django-scarface <https://pypi.python.org/pypi/django-scarface>`_

  - Downsides:

    + Like django-push-notifications but worse (requires Amazon SNS)


Actually Not Similar Projects
-----------------------------

There's also a good number of notification frameworks that solve a
seeming-ly similar, but different problem: in-app notifications and
activity feeds. These are the sort of things that might be a back-end
to Django Vox. They're listed here for completion:

* `django-notifications-hq <https://pypi.python.org/pypi/django-notifications-hq>`_
* `Stream Django (getstream.io) <https://pypi.python.org/pypi/stream-django>`_
* `Stream Framework <https://pypi.python.org/pypi/stream_framework>`_
* `django-notify-x <https://pypi.python.org/pypi/django-notify-x>`_
* `Django Messages Extends <https://pypi.python.org/pypi/django-messages-extends>`_
* `django-stored-messages <https://pypi.python.org/pypi/django-stored-messages/1.4.0>`_
* `django-user-streams <https://pypi.python.org/pypi/django-user-streams>`_
* `django-knocker <https://pypi.python.org/pypi/django-knocker>`_
* `django-subscription <https://pypi.python.org/pypi/django-subscription>`_
* `django-offline-messages <https://pypi.python.org/pypi/django-offline-messages>`_
* `Django webline Notifications <https://pypi.python.org/pypi/django-webline-notifications>`_
* `django-nyt <https://pypi.python.org/pypi/django-nyt>`_

Also, of honorable mention is `Kawasemi <https://pypi.python.org/pypi/kawasemi/>`_
which is more of a logging system than anything else.


