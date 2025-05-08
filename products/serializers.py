from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'RFID', 'bought_price', 'selling_price', 'shop']
        read_only_fields = ['created_at']

    def validate_bought_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bought price must be positive")
        return value

    def validate_selling_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Selling price must be positive")
        return value

    def validate(self, data):
        bought = data.get('bought_price')
        selling = data.get('selling_price')
        if bought and selling and selling < bought:
            raise serializers.ValidationError("Selling price cannot be less than bought price")
        return data
