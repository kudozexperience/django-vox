import django.conf

BACKENDS = getattr(django.conf.settings,
                   'DJANGO_COURIER_BACKENDS', (
                       'django_courier.backends.EmailBackend',
                       'django_courier.backends.TwilioBackend',
                       'django_courier.backends.SlackWebhookBackend',
                       # disabled because it's not stable/tested
                       # 'django_courier.backends.PostmarkTemplateBackend',
                   ))
