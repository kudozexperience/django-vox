=======================
Protocols and Addresses
=======================

A protocol is what lets us sort out and make sense of contact information
in django-vox. Classic examples of a "protocol" are things like email,
SMS, and XMPP. You can also have proprietary protocols like Slack webhooks,
or things that use Google or Apple's push notifications.

Each protocol has it's own kind of addresses. When a contact is sent a
message, django-vox automatically selects a backend that matches the
available contacts (and addresses by extension) for that protocol.

Activity
========

ID: ``activity``

This protocol is for `Activity Streams`_ (and only slightly supported
`ActivityPub`_). Message are stored locally in the database and are retrievable
from an inbox. Setting this up is a bit of work, see the section on
:doc:`activities`.

.. _Activity Streams: https://www.w3.org/TR/activitystreams-core/
.. _ActivityPub: https://www.w3.org/TR/2018/REC-activitypub-20180123/

Email
=====

ID: ``email``

The email protocol is really straightforward, the contact's address
is just the email address.


SMS
===

ID: ``sms``

The contact's address for SMS is the contact's phone number in E.164 format.
It's recommended to use ``django-phonenumber-field`` if you want to store
these numbers in a database.


Twitter
=======

Addresses for the twitter protocol can take two forms:

  1. An empty string means the message will get posted as a status update
     for the account specified in the setting.
  2. Anything else will be sent as a direct message to the user with that
     handle. You shouldn't prefix an '@' to the address and you need to
     have the correct permissions set in order for this to work.


Webhook Protocols
=================

While webhooks aren't typically a convenient way to contact end-users, they
can be pretty useful for setting up site contacts. Because of the templating
system, you can be quite flexible in the way you set them up.

=============  =================  =========================
Name           ID                 Purpose
=============  =================  =========================
JSON Webhook   ``json-webhook``   Generic JSON data
                                  (specified in template)
Slack Webhook  ``slack-webhook``  Posting messages to Slack
=============  =================  =========================

XMPP
====

XMPP (or Jabber) is a standardized, decentralized chat system. The contact's
address should just be their XMPP address (or JID, as it's sometimes called).