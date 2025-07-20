from django.urls import path

from .views import sell_products_view, sell_scanned_products_view, refund_product_view, lookup_refund_rfid, \
    refund_scanned_products, confirm_sold_products

urlpatterns = [
    path('sell/', sell_products_view, name='sell_products'),
    path('sell/confirm/', sell_scanned_products_view, name='sell_scanned_products'),
    path('refund/', refund_product_view, name='refund_page'),
    path('refund/lookup/', lookup_refund_rfid, name='lookup_refund_rfid'),
    path('refund/process/', refund_scanned_products, name='refund_scanned_products'),
    path('confirm-sold-products/', confirm_sold_products, name='confirm_sold_products'),
]
