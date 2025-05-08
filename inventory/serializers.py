# inventory/serializers.py
from products.serializers import ProductSerializer
from shops.serializers import ShopSerializer
from .models import ProductInstance
from rest_framework import serializers
from .models import ShopInventory


class ProductInstanceSerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested product data
    shop = ShopSerializer()  # Nested shop data

    class Meta:
        model = ProductInstance
        fields = ['id', 'product', 'rfid', 'shop', 'status', 'created_at']


class ShopInventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer()  # Nested product data
    shop = ShopSerializer()  # Nested shop data

    class Meta:
        model = ShopInventory
        fields = ['id', 'shop', 'product', 'stock_quantity']
