# -*- coding: utf-8 -*-

import django.urls
from django.db import connections, transaction


# copied from django
def make_view_atomic(view):
    non_atomic_requests = getattr(view, '_non_atomic_requests', set())
    for db in connections.all():
        if (db.settings_dict['ATOMIC_REQUESTS'] and
                db.alias not in non_atomic_requests):
            view = transaction.atomic(using=db.alias)(view)
    return view


def activity_inbox_middleware(get_response):
    def middleware(request):
        # setting request.urlconf doesn't work because that screws up
        # calls to reverse() within the normal django app
        if 'application/activity+json' in request.META.get('HTTP_ACCEPT', ''):
            urlconf = 'django_vox.activity_urls'
            resolver = django.urls.get_resolver(urlconf)
            resolver_match = resolver.resolve(request.path_info)
            callback, callback_args, callback_kwargs = resolver_match
            request.resolver_match = resolver_match

            wrapped_callback = make_view_atomic(callback)
            return wrapped_callback(request, *callback_args,
                                    **callback_kwargs)

        return get_response(request)

    return middleware
