CHANGES
=======

4.0.6
-----

* Fix a bug where a contact could get the same notification twice

4.0.5
-----

* Fix another circular import dependency issue

4.0.4
-----

* Fix a potential circular import dependency issue

4.0.3
-----

* Fix a bug with get_recipient_choices ignoring the registered channels

4.0.2
-----

* Fix a bug when Notification.issue is passed SimpleLazyObject

4.0.1
-----

* Fix a bug with ``Channel.field``

4.0
---

This version includes a new registration system for models so that you
don’t have to subclass ``VoxModel`` (which is a problem for 3rd party models).
The new way of registering the models is described in detail in the
documentation.

Incompatibilities with Version 3:

* The actor & target arguments on ``Notification.issue`` must be specified
  by keyword arguments now. This doesn’t affect
  ``VoxModel.issue_notification``, so it’s only relevant if you were manually
  loading Notifications and triggering them.
* A few default backends were are no longer defaults

Other changes:

* Backend settings can just reference the class, and not the module
* Notify will use a default address if none is specified
* Notifications now have a “last updated” field

3.6
---

* Fix bug in notification editor where switching one template's backend would
  alter the state of the another template form.
* Add more tests
* Make ``Backend.send_message`` an instance method, and instantiate backend
  objects when sending messages. This is a significant API change, but it's
  unlikely to actually cause backwards compatibility issues.
* Add title to notify page

3.5.3
-----

* Fix bugs in demo caused by slug
* Add icon

3.5.2
-----

* Add better support and testing for non-ID primary keys

3.5.1
-----

* Fix packaging problem (missing files)

3.5
---

* Fix some javascript problems on Django 2.1 & 2.2
* Add one-time message admin actions

3.4
---

* Fix crash when a non VoxModel model is registered

3.3
---

* Pin to a newer version of august, it works much better
* Be slightly more sophisticated with our activity data parsing

3.2
---

* fix implementation of activity\_type parameter
* Fix bug issuing notifications with non VoxModel objects
* Fix bug where django will crash if ``to_addresses`` is a generator
* Omit skipping message when notification is not from code
* Fix bug where we kept recreating notifications
* Keep orphaned notifications with templates so we don't delete data

3.1
---

* Add ability to remove notifications of deleted classes
* Fix error in notification editor when using grappelli

3.0
---

* Rewrite that add support for multiple participants

2.3
---

* add ``read_at`` field on inbox items
* Users should be posting read activities to outbox, duh

2.2
---

* Add the ability to post to inboxes and read messages

2.1
---

* Redo activity schema so that its more straightforward
* fix bug in ``background_task`` implementation

2.0.0
-----

* Add activity backend

1.1.0
-----

* Replace newlines in subject with space
* Add support for resending failed messages
* A few improvements to the admin
* Add Grappelli compatibility

1.0.0
-----

First stable release

