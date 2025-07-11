from django.urls import path

from .rfid_reader import current_sold_products
from .views import ProductCreateAPIView, ProductListAPIView, ProductDetailView, generate_barcode_view, \
    print_product_barcode_view, bind_rfid_view, choose_quantity_view, cancel_print_session, check_rfid_view, \
    lookup_rfid_view, cancel_print_session_view, bind_rfid_page_view, ProductUpdateView, ProductDeleteView, \
    current_products

urlpatterns = [
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('all', ProductListAPIView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:pk>/edit/', ProductUpdateView.as_view(), name='edit-product'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete-product'),
    path('api/generate-barcode/', generate_barcode_view, name='generate-barcode'),
    path('<int:pk>/print-barcode/', print_product_barcode_view, name='print_barcode'),
    path('<int:pk>/bind-rfid/', bind_rfid_view, name='bind_rfid'),
    path('choose-quantity/<int:pk>/', choose_quantity_view, name='choose_quantity'),
    path('cancel-print-session/', cancel_print_session, name='cancel_print_session'),
    path("check-rfid/", check_rfid_view, name="check_rfid"),
    path("current-products/", current_products, name="current_products"),
    path("lookup-rfid/", lookup_rfid_view, name="lookup_rfid"),
    path('<int:pk>/bind-rfid-page/', bind_rfid_page_view, name='bind_rfid_page'),
    path('cancel-print-session/', cancel_print_session_view, name='cancel_print_session'),
path('products/current-sold-products/', current_sold_products, name='current_sold_products'),

]
