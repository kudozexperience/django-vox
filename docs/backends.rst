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

    # adds dependencies for html email backend and the twilio backend
    pip3 install django-vox[html,twilio]

In order to add or remove backends, you need to set the
``DJANGO_VOX_BACKENDS`` setting in your projects ``settings.py``
file. The setting is a list of class names for backends that are
in-use/enabled. If not set, the default is (assuming you have the
required dependencies)::

    DJANGO_VOX_BACKENDS = (
        'django_vox.backends.EmailBackend',
        'django_vox.backends.MarkdownEmailBackend',
        'django_vox.backends.HtmlEmailBackend',
        'django_vox.backends.TwilioBackend',
        'django_vox.backends.SlackWebhookBackend',
    )

Django-vox provides a few built-in backends. Here's how to
set them up and use them.

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

Class
    ``django_vox.backends.html_email.Backend``
Extra
  ``[html]``

When using this, the content of your template will have to be HTML. If
you don't, it will be HTML anyways, but it will look real bad, and the
god will frown on you. The backend automatically uses a library to
convert the HTML into plain-text, so that there is a text version of the
email, and so that the spam filters think better of you.

Incidentally, the subject field is not HTML formatted.

Markdown Email Backend
~~~~~~~~~~~~~~~~~~~~~~

Class
    ``django_vox.backends.markdown_email.Backend``
Extra
 ``[markdown]``

This backend has you specify the content of your templates with markdown.
While markdown doesn't give you quite the flexibility as HTML, it's a bit
more intuitive.

Template-based Email Backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Class
    ``django_vox.backends.template_email.Backend``

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

Class
    ``django_vox.backends.postmark_email.Backend``

This backend requires one config setting: ``POSTMARK_API_TOKEN``. It should
be, unsurprisingly, your token for interacting with the postmark API. When
using this backend, the 'Subject' field refers to Postmark's "template alias"
and the template content should look something like this::

    parameter_one: {{ content.attribute }}
    parameter_two: {{ recipient.name }}


Twilio
------

Protocol
  ``sms``
Class
    ``django_vox.backends.twilio.Backend``
Extra
  ``[twilio]``

The twilio backend uses Twilio's python library. It depends on 3 settings,
all of which needs to be set for proper functioning.

======================  ================================================
``TWILIO_ACCOUNT_SID``  Twilio account ID (required for Twilio backend)
``TWILIO_AUTH_TOKEN``   Twilio authentication token (required for Twilio
                        backend)
``TWILIO_FROM_NUMBER``  Phone # to send Twilio SMS from (required for
                        Twilio backend)
======================  ================================================

Webhook (JSON)
--------------

Protocol
  ``json-webhook``
Class
    ``django_vox.backends.json_webhook.Backend``

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
Class
    ``django_vox.backends.slack.Backend``

This backend requires no configuration in django, all of the configuration
is essentially part of the addresses used in the protocol. For setting up
slack-webhook addresses, see the documentation on :doc:`protocols <protocols>`.


.. _django settings: https://docs.djangoproject.com/en/1.11/ref/settings/
