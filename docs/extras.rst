======
Extras
======

Background Tasks
================

Django vox can integrate with `django-backgroundtasks`_ if available.
Doing so is pretty simple, and (particularly if you have to do database
lookups inside ``get_contacts_for_notification``) can significantly reduce
the work for an initial request.


Setup
-----

In order to get this set up, you first need to go install and configure
django-backgroundtasks yourself. It's fairly straightforward, but exactly
how you want the background tasks run is a question only you can answer.

Once it is set up, replace the following::

    from django_vox.models import VoxModel

with this::

    from django_vox.extra.background import BackgroundVoxModel \
        as VoxModel



Troubleshooting
---------------

If your messages aren't being sent out, there's a good chance that your
background tasks just aren't getting run at all. Try running
``manage.py process_tasks`` or check your queued background tasks in the
django admin.

.. _django-backgroundtasks: https://pypi.org/project/django-background-tasks/

