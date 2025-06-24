from django.apps import AppConfig
from django.core.cache import cache

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Start RFID reader when Django starts
        if not cache.get('rfid_reader_started'):
            from .rfid_reader import start_rfid_reader
            if start_rfid_reader():
                cache.set('rfid_reader_started', True, timeout=None)
