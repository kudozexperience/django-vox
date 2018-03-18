from django.apps import AppConfig


class CourierConfig(AppConfig):
    name = 'django-courier'
    verbose_name = 'Courier'

    def ready(self):
        pass
