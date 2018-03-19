Protocols and Addresses
=======================

A protocol is what lets us sort out and make sense of contact information
in django-courier. Classic examples of a "protocol" are things like email,
SMS, and XMPP. You can also have proprietary protocols like Slack webhooks,
or things that use Google or Apple's push notifications.

Each protocol has it's own kind of addresses. When a contact is sent a
message, django-courier automatically selects a backend that matches the
available contacts (and addresses by extension) for that protocol.

Email
-----

ID: ``email``

The email protocol is really straightforward, the contact's address
is just the email address.


SMS
---

ID: ``sms``

The contact's address for SMS is the contact's phone number in E.164 forat.
It's recommended to use ``django-phonenumber-field`` if you want to store
these numbers in a database.


Slack Webhook
-------------

ID: ``slack-webhook``

The address of a slack webhook is the URL of the webhook. This is mostly
intended to be used in conjunction with site contacts because of the
obvious difficulty of creating webhooks for slack channels.

