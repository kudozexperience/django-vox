from django.apps import AppConfig

from django.test.utils import setup_test_environment, setup_databases


class CourierTestConfig(AppConfig):
    name = 'tests'
    verbose_name = 'Courier Test'

    AUTHOR_EMAIL = 'author@example.org'
    AUTHOR_NAME = 'Author'
    AUTHOR_PASSWORD = 'password'

    def ready(self):
        setup_test_environment()
        setup_databases(verbosity=3, interactive=False)
        from django_courier.management.commands.make_notifications \
            import make_notifications
        make_notifications(self)
        from .models import User
        try:
            User.objects.get(email=self.AUTHOR_EMAIL)
        except User.DoesNotExist:
            User.objects.create_superuser(
                self.AUTHOR_EMAIL, self.AUTHOR_NAME, self.AUTHOR_PASSWORD)
