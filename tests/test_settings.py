from django.test.utils import override_settings

import django_vox.settings


def test_backends():
    with override_settings(DJANGO_VOX_BACKENDS=None):
        backends = django_vox.settings.BACKENDS
        # we should have all the backend dependencies installed for
        # testing purposes
        expected = [
            'django_vox.backends.html_email.Backend',
            'django_vox.backends.markdown_email.Backend',
            'django_vox.backends.postmark_email.Backend',
            'django_vox.backends.template_email.Backend',
            'django_vox.backends.twilio.Backend',
            'django_vox.backends.twitter.Backend',
            'django_vox.backends.slack.Backend',
            'django_vox.backends.json_webhook.Backend',
            'django_vox.backends.xmpp.Backend',
        ]
        assert expected == backends
