Backends
========

A backend is what is responsible for sending the actual messages.
A backend implements a "protocol" like email or SMS. Multiple backends
might implement the same protocol, so you might have a backend that
sends email via SMTP, and another one that uses the mailgun API. The
important thing is that all the backends implementing a specific
protocol must accept the same form of addresses.

In order to add or remove backends, you need to set the
``DJANGO_COURIER_BACKENDS`` setting in your projects ``settings.py``
file. The setting is a list of class names for backends that are
in-use/enabled. If not set, the default is::

    DJANGO_COURIER_BACKENDS = (
        'django_courier.backends.EmailBackend',
        'django_courier.backends.TwilioBackend',
        'django_courier.backends.SlackWebhookBackend',
    )

Django-courier provides a few built-in backends. Here's how to
set them up and use them.

Email
-----

Protocol: ``email``

The email backend is a wrapper around Django's internal mailing system.
As such, it uses all of the built-in email settings including
``DEFAULT_FROM_EMAIL``, and everything that starts with ``EMAIL`` in
the standard `django settings`_.

Writing notification templates for emails are a little more complicated
than they are for the other backends, because emails can have multiple
parts to them (subject, text, and html). The details of this are covered
in the section on :doc:`templates <templates>`.

Twilio
------

Protocol: ``sms``

The twilio backend uses Twilio's python library. It depends on 3 settings,
all of which needs to be set for proper functioning.

======================  ================================================
``TWILIO_ACCOUNT_SID``  Twilio account ID (required for Twilio backend)
``TWILIO_AUTH_TOKEN``   Twilio authentication token (required for Twilio
                        backend)
``TWILIO_FROM_NUMBER``  Phone # to send Twilio SMS from (required for
                        Twilio backend)
======================  ================================================

Slack Webhook
-------------

Protocol: ``slack-webhook``

This backend requires no configuration in django, all of the configuration
is essentially part of the addresses used in the protocol. For setting up
slack-webhook addresses, see the documentation on :doc:`protocols <protocols>`.


.. _django settings: https://docs.djangoproject.com/en/1.11/ref/settings/
