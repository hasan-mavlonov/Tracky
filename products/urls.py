# products/urls.py
from django.urls import path
from .views import ProductCreateAPIView, ProductListAPIView, ProductDetailAPIView

urlpatterns = [
    path('products/create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('products/all', ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
]
