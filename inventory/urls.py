# inventory/urls.py
from django.urls import path
from .views import ProductInstanceCreateAPIView, ProductInstanceListAPIView, ProductInstanceDetailAPIView

urlpatterns = [
    path('all/', ProductInstanceListAPIView.as_view(), name='product-instance-list'),
    path('<int:id>/', ProductInstanceDetailAPIView.as_view(), name='product-instance-detail'),
    path('create/', ProductInstanceCreateAPIView.as_view(), name='create-product-instance'),
]
