Running the Demo
================

The project comes with a demo that can be run from the project directory
using::

    make demo

The demo runs with everything in memory, so as soon as you stop it,
everything you've done to it will be gone! It uses django's development
server, so if you change the source files, the server will reload and
any data you had will get reset.

The Jist
--------

The demo is a really basic blog app with the ability for people to
"subscribe" by adding their email address and name. Subscribers
get emailed, whenever a new article is posted, and the email
contains a link that lets them comment. The article's author gets
notified whenever comments are posted. Finally, there's also a site
contact that gets notified whenever a new subscriber is added.

The demo is set up with django's console email backend, so all the
email notifications are printed to the console, where you can see
what is going on.

Walkthrough
-----------

You can use the demo however you want, but in case you're lost,
here's a walkthough you can follow that will show you its features.

1. First, go to the admin site. The url should be
   ``http://127.0.0.1:8000/admin/``. The username is ``author@example.org``
   and the password is ``password``. Once in, you can go to "Articles"
   (under Vox Demo) and add a new one.
2. The demo comes with a subscriber already added, so once you add the
   article, an email should show up the console. The
   email contains a link to the new article. Click (or copy-paste) the
   link to open it in a browser. The loaded page should display the
   added article and an "add a comment" section. Go ahead and add a
   comment. After adding a comment you should see another email in the
   console addressed to the article's author.
3. Additionally, if you go to the blog's index (``http://127.0.0.1:8000/``),
   you'll see a form to subscribe to the blog. If you add a subscriber,
   you'll get another email in the console notifying the site contact that
   somebody subscribed.
4. Finally, you can look though the admin to see how things are set up.
   You can alter the site contacts or play with the notifications and
   templates. Bare in mind that while all the backends are enabled, and
   selectable, the users only have email contacts, so the other backends
   won't do anything for anything besides site contacts.

