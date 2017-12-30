from django.apps import AppConfig


class NotifyConfig(AppConfig):
    name = 'django-notify'
    verbose_name = 'Notify'

    def ready(self):
        pass

