Backends
========

A backend is what is responsible for sending the actual messages.
A backend implements a "protocol" like email or SMS. Multiple backends
might implement the same protocol, so you might have a backend that
sends email via SMTP, and another one that uses the mailgun API. The
important thing is that all the backends implementing a specific
protocol must accept the same form of addresses.

Most of these backends require extra dependencies that are not required
for the base package. The specific extras are listed in the documentation,
and you can mix/match them. For example::

    # adds dependencies for markdown email, xmpp, twitter and the twilio
    # backends
    pip3 install django-vox[xmpp,markdown,twitter,twilio]

In order to add or remove backends, you need to set the
``DJANGO_VOX_BACKENDS`` setting in your projects ``settings.py``
file. The setting is a list of module names for backends that are
in-use/enabled. If not set, the default is (assuming you have the
required dependencies)::

    DJANGO_VOX_BACKENDS = (
        "django_vox.backends.markdown_email",
        "django_vox.backends.template_email",
        "django_vox.backends.twilio",
        "django_vox.backends.twitter",
        "django_vox.backends.xmpp",
        # This backend requires lot of setup
        # "django_vox.backends.activity",
        # this backend is not very user-friendly
        # "django_vox.backends.html_email",
        # disabled because they're proprietary or not commonly used
        # "django_vox.backends.postmark_email",
        # "django_vox.backends.slack",
        # "django_vox.backends.json_webhook",
    )

Django-vox provides a few built-in backends. Here's how to
set them up and use them.

Activity Backend
----------------

Protocol
  ``activity``
Module
    ``django_vox.backends.activity``

This is the backend for Activity Streams support. Setup is covered on
the :doc:`activities` page.

Email Backends
--------------

Protocol
  ``email``

These backends are a wrapper around Django's internal mailing system.
As such, it uses all of the built-in email settings including
``DEFAULT_FROM_EMAIL``, and everything that starts with ``EMAIL`` in
the standard `django settings`_.

There are 3 backends included:

* One that uses HTML (and converts it to text for you)
* One that uses Markdown (and coverts it to HTML for you)
* One that uses Django template blocks to specify both HTML & text
  (not recommended)

HTML Email Backend
~~~~~~~~~~~~~~~~~~

Module
    ``django_vox.backends.html_email``

When using this, the content of your template will have to be HTML. If
you don't, it will be HTML anyways, but it will look real bad, and the
god will frown on you. The backend automatically uses a library to
convert the HTML into plain-text, so that there is a text version of the
email, and so that the spam filters think better of you.

Incidentally, the subject field is not HTML formatted.

Markdown Email Backend
~~~~~~~~~~~~~~~~~~~~~~

Module
    ``django_vox.backends.markdown_email``
Extra
 ``[markdown]``

This backend has you specify the content of your templates with markdown.
While markdown doesn't give you quite the flexibility as HTML, it's a bit
more intuitive.

Template-based Email Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Module
    ``django_vox.backends.template_email``

This backend isn't recommended because it's probably too confusing to be
wroth it. However, if you really need to tailor-make your emails, it's
a solution that you can make work.

Writing notification templates for emails are a little more complicated
than they are for the other backends, because emails can have multiple
parts to them (subject, text, and html). The basic form looks like this::

    {% block subject %}Email Subject{% endblock %}
    {% block text_body %}Text body of email{% endblock %}
    {% block html_body %}HTML body of email{% endblock %}

Postmark Templates
------------------

Module
    ``django_vox.backends.postmark_email``

This backend requires one config setting: ``DJANGO_VOX_POSTMARK_TOKEN``. It
should be, unsurprisingly, your token for interacting with the postmark API.
When using this backend, the 'Subject' field refers to Postmark's "template
alias" and the template content should look something like this::

    parameter_one: {{ content.attribute }}
    parameter_two: {{ recipient.name }}

Twilio
------

Protocol
  ``sms``
Module
    ``django_vox.backends.twilio``
Extra
  ``[twilio]``

The twilio backend uses Twilio's python library. It depends on 3 settings,
all of which needs to be set for proper functioning.

=================================  ===============================
``DJANGO_VOX_TWILIO_ACCOUNT_SID``  Twilio account ID
``DJANGO_VOX_TWILIO_AUTH_TOKEN``   Twilio authentication token
``DJANGO_VOX_TWILIO_FROM_NUMBER``  Phone # to send Twilio SMS from
=================================  ===============================

Twitter
-------

Protocol
  ``twitter``
Module
    ``django_vox.backends.twitter``
Extra
  ``[twitter]``

The twitter backend allows you to post updates to twitter and (with the
right permissions), send direct messages to your followers. In order to
set it up, you first need to create a twitter application. The
`python-twitter docs`_ explain the process well. Note that you can
ignore callback URL, and you'll want to set the name, description, and
website fields to the name, description, and website of your application.

Once you're done that, you may want to turn on "Read, Write and Access
direct messages" in the "Permissions" tab. Then generate/regenerate your
access token and secret.

Once you're done that, you'll want to set the following values in your
settings.py file:

======================================  ============================
``DJANGO_VOX_TWITTER_CONSUMER_KEY``     Consumer Key (API Key)
``DJANGO_VOX_TWITTER_CONSUMER_SECRET``  Consumer Secret (API Secret)
``DJANGO_VOX_TWITTER_TOKEN_KEY``        Access Token
``DJANGO_VOX_TWITTER_TOKEN_SECRET``     Access Token Secret
======================================  ============================

.. note::
   In order to post a message to your wall, make a site contact with
   the the twitter protocol and a *blank* address. In order to send a
   direct message, you'll need a address that equals your user's twitter
   handle (not including the "@" prefix).

Webhook (JSON)
--------------

Protocol
  ``json-webhook``
Module
    ``django_vox.backends.json_webhook``

This backend post JSON-formatted data to webhook. It's useful for
implementing generic webhooks or integrating with systems like
Huginn or Zapier. The way you specify parameters is the same
as with the Postmark backend::

    parameter_one: {{ content.attribute }}
    parameter_two: Hello World

This will translate into::

    {'parameter_one': '<content.attribute>',
     'parameter_two': 'Hello World'}

Webhook (Slack)
---------------

Protocol
  ``slack-webhook``
Module
    ``django_vox.backends.slack``

This backend requires no configuration in django, all of the configuration
is essentially part of the addresses used in the protocol. For setting up
slack-webhook addresses, see the documentation on :doc:`protocols <protocols>`.


XMPP
-------

Protocol
  ``xmpp``
Module
    ``django_vox.backends.xmpp``
Extra
  ``[xmpp]``

This backends lets you send messages over xmpp to other xmpp users. It's
pretty straightforward; however, it's also pretty slow right now, so
don't use it unless your also doing notifications in the background.

To set this up, you need to have the XMPP address and password in your
settings. Here's the relevant settings.

============================  ============
``DJANGO_VOX_XMPP_JID``       XMPP address
``DJANGO_VOX_XMPP_PASSWORD``  Password
============================  ============

.. _django settings: https://docs.djangoproject.com/en/1.11/ref/settings/
.. _python-twitter docs: https://python-twitter.readthedocs.io/en/latest/getting_started.html
