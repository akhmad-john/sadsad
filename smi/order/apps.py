from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'smi.order'

    def ready(self):
        import smi.order.receivers
