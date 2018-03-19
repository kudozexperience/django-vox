from django.apps import AppConfig
from django.core.management import call_command
from django.test.utils import setup_databases, setup_test_environment


class CourierTestConfig(AppConfig):
    name = 'tests'
    verbose_name = 'Courier Test'

    def ready(self):
        pass


class CourierDemoConfig(AppConfig):
    name = 'tests'
    verbose_name = 'Courier Demo'

    def ready(self):
        setup_test_environment()
        setup_databases(verbosity=3, interactive=False)
        # add notification objects
        from django_courier.management.commands.make_notifications \
            import make_notifications
        make_notifications(self)
        call_command('loaddata', 'demo')
