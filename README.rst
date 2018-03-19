==============
Django Courier
==============

|pipeline-badge| |coverage-badge| |docs-badge|

Django courier is a django app that allow you to create and issue
different types of notifications. Notifications can have different
kinds of parameters which allow for convenient editing in the admin.

Installation
------------

First, install via pip (on Windows, replace ``pip3`` with ``pip``)

::

  pip3 install django-courier

Then, edit your ``settings.py``, adding this line to ``INSTALLED_APPS``

::

      'django_courier',

Features
--------

To be completed


Settings
--------

This app makes use of the following settings. They can be set in your app's ``settings.py``:

=======================  =======================================================================
DEFAULT_FROM_EMAIL       Address to send emails from (standard django setting)
TWILIO_ACCOUNT_SID       Twilio account ID (required for Twilio backend)
TWILIO_AUTH_TOKEN        Twilio authentication token (required for Twilio backend)
TWILIO_FROM_NUMBER       Phone # to send Twilio SMS from (required for Twilio backend)
DJANGO_COURIER_BACKENDS  List of class names for backends that are in-use/enabled (not required)
=======================  =======================================================================

TODO
----

  * Show model parameters in admin


.. |pipeline-badge| image:: https://gitlab.com/alantrick/django-courier/badges/master/pipeline.svg
   :target: https://gitlab.com/alantrick/django-courier/
   :alt: Documentation Status

.. |coverage-badge| image:: https://gitlab.com/alantrick/django-courier/badges/master/coverage.svg
   :target: https://gitlab.com/alantrick/django-courier/
   :alt: Documentation Status

.. |docs-badge| image:: https://readthedocs.org/projects/djangocourier/badge/?version=latest
   :target: http://djangocourier.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
