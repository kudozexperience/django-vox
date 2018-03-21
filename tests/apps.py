from django.apps import AppConfig
from django.core.management import call_command
from django.test.utils import setup_databases


class CourierTestConfig(AppConfig):
    name = 'tests'
    verbose_name = 'Courier Test'

    def ready(self):
        setup_databases(verbosity=3, interactive=False)


class CourierDemoConfig(AppConfig):
    name = 'tests'
    verbose_name = 'Courier Demo'

    def ready(self):
        setup_databases(verbosity=3, interactive=False)
        # add notification objects
        from django_courier.management.commands.make_notifications \
            import make_notifications
        make_notifications(self)
        call_command('loaddata', 'demo')
