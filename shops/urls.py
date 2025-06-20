from django.urls import path
from .views import ShopListAPIView, ShopCreateAPIView, ShopDetailAPIView

urlpatterns = [
    path('create/', ShopCreateAPIView.as_view(), name='shop-create'),
    path('all', ShopListAPIView.as_view(), name='shop-product-list'),
    path('<int:id>/', ShopDetailAPIView.as_view(), name='shop-detail'),
]
