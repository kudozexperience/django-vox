==========
Django Vox
==========

|pipeline-badge| |coverage-badge| |docs-badge| |pypi-badge|

Django vox is a django app that allow you to create and issue
different types of notifications. Notifications can have different
kinds of parameters which allow for convenient editing in the admin.


Why this exists
---------------

TLDR: Because I am lazy and I don't want to spend my evening doing
a deploy just because marketing wants to update the text in their
latest spam mail.

In a few more words:

* Editing copy for notifications shouldn't have to be done by programmers.
  This means:

  1. The notification templates should be editable in the admin
  2. The information necessary to correctly make a template, whether
     it's a template ID or parameters) should be available in the admin
     page. It shouldn't be necessary to look through source code just to
     make a notification work.
  3. Number 2 is actually a fairly difficult problem.

* People have different ways of interacting with computers, and one
  way of doing notifications (i.e. email) doesn't always make sense.

  1. Added to that, sending a text message that's as verbose as an HTML
     email is simply ridiculous. Each medium begets its own kind of
     content.
  2. Since, as we mentioned earlier, content should be manageable
     by non-programmers, the different ways of sending messages should
     be manageable by non-programmers.


I want it, stat!
----------------

Well, why don't you just head over to `the documentation`_ and we'll
get you started. A word of warning, it's not super simple to setup, but
it's worth it.


.. |pipeline-badge| image:: https://gitlab.com/alantrick/django-vox/badges/master/pipeline.svg
   :target: https://gitlab.com/alantrick/django-vox/
   :alt: Build Status

.. |coverage-badge| image:: https://gitlab.com/alantrick/django-vox/badges/master/coverage.svg
   :target: https://gitlab.com/alantrick/django-vox/
   :alt: Coverage Status

.. |docs-badge| image:: https://img.shields.io/readthedocs/django-vox.svg
   :target: `the documentation`_
   :alt: Documentation

.. |pypi-badge| image:: https://img.shields.io/pypi/v/django_vox.svg
   :target: https://pypi.org/project/django-vox/
   :alt: Project on PyPI

.. _the documentation: http://django-vox.readthedocs.io/en/latest/?badge=latest

