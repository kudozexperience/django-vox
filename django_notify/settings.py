import django.conf

BACKENDS = getattr(django.conf.settings,
                   'DJANGO_NOTIFY_BACKENDS', (
                       'django_notify.models.EmailBackend',
                       'django_notify.models.TwilioBackend',
                       # disabled because it's not stable/tested
                       # 'django_notify.models.PostmarkTemplateBackend',
                   ))
