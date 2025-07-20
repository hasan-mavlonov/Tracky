from django.urls import path

from .views import (
    ProductCreateAPIView,
    ProductListView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView,
    print_product_barcode_view,
    bind_rfid_view,
    bind_rfid_page_view,
    choose_quantity_view,
    cancel_print_session_view,
    check_rfid_view,
    lookup_rfid_view,
    store_rfids_view,
    current_products,
    current_sold_products,
)

urlpatterns = [
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('all/', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('check-rfid/', check_rfid_view, name='check_rfid'),
    path('<int:pk>/print-barcode/', print_product_barcode_view, name='print_barcode'),
    path('<int:pk>/bind-rfid/', bind_rfid_view, name='bind-rfid'),
    path('<int:pk>/bind-rfid-page/', bind_rfid_page_view, name='bind-rfid-page'),
    path('<int:pk>/choose-quantity/', choose_quantity_view, name='choose-quantity'),
    path('cancel-print-session/', cancel_print_session_view, name='cancel-print-session'),
    path('lookup-rfid/', lookup_rfid_view, name='lookup-rfid'),
    path('store-rfids/', store_rfids_view, name='store-rfids'),
    path('current-products/', current_products, name='current-products'),
    path('current-sold-products/', current_sold_products, name='current-sold-products'),
]
