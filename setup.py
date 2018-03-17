#!/usr/bin/env python3
import os
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='django-courier',
    version='0.5.4',
    description='A notification app for Django',
    long_description=read('README.rst'),
    author='Alan Trick',
    author_email='me@alantrick.ca',
    url='https://bitbucket.org/alantrick/django-courier',
    packages=[
        'django_courier',
        'django_courier.migrations',
        'django_courier.management.commands',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Topic :: Utilities',
    ],
    install_requires=[
        'Django>=1.11,<2.0',
        'django-anymail',
        'djangorestframework',
        'twilio',
        'requests',
    ],
    extras_require={
        'test': ['pytest', 'pytest-django'],
    },
    license='LGPL',

)
