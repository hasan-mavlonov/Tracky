from django.urls import path
from .views import ProductCreateAPIView, ProductListAPIView, ProductDetailAPIView, generate_barcode_view, \
    print_product_barcode_view

urlpatterns = [
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('all', ProductListAPIView.as_view(), name='product-list'),
    path('<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('api/generate-barcode/', generate_barcode_view, name='generate-barcode'),
    path('<int:pk>/print-barcode/', print_product_barcode_view, name='print-barcode'),
]
