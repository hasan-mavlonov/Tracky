# sales/urls.py

from django.urls import path
from .views import scan_rfid_view, register_sale_view

urlpatterns = [
    path('scan/', scan_rfid_view, name='scan_sale'),
    path('register/', register_sale_view, name='register_sale'),
]
