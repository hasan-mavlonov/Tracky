from django.urls import path
from .views import sell_products_view, sell_scanned_products_view

urlpatterns = [
    path('sell/', sell_products_view, name='sell_products'),
    path('sell/confirm/', sell_scanned_products_view, name='sell_scanned_products'),
]
