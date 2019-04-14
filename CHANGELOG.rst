CHANGES
=======

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

