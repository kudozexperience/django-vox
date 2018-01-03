import django.conf

BACKENDS = getattr(django.conf.settings,
                   'DJANGO_COURIER_BACKENDS', (
                       'django_courier.models.EmailBackend',
                       'django_courier.models.TwilioBackend',
                       # disabled because it's not stable/tested
                       # 'django_courier.models.PostmarkTemplateBackend',
                   ))
