Installation
============

Getting the code
----------------

The recommended way to install django-courier is via pip_ (on Windows,
replace ``pip3`` with ``pip``) ::

    $ pip3 install django-courier

.. _pip: https://pip.pypa.io/


Configuring Django
------------------

Add ``'django_courier'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        'django_courier',
    ]

Additionally, you may want to configure certain :doc:`backends <backends>`
depending on exactly what sort of other notifications you want.


