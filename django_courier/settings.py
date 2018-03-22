import django.conf

BACKENDS = getattr(django.conf.settings, 'DJANGO_COURIER_BACKENDS', None)
if BACKENDS is None:
    # Automatically set based on libraries available
    BACKENDS = ['django_courier.backends.EmailBackend',
                'django_courier.backends.SlackWebhookBackend']
    try:
        import twilio.rest  # noqa: F401
        BACKENDS.append('django_courier.backends.TwilioBackend')
    except ImportError:
        pass
