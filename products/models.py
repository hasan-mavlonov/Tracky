# products/models.py
from django.db import models

from shops.models import Shop


class Product(models.Model):
    """Represents a product type with common attributes"""
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, unique=True)  # Shared across all instances
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['barcode']),
        ]

    def __str__(self):
        return f"{self.name} ({self.barcode})"

class ProductInstance(models.Model):
    """Represents a physical item with unique RFID"""
    RFID = models.CharField(max_length=100, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='instances')
    status = models.CharField(
        max_length=10,
        choices=[
            ('IN_STOCK', 'In Stock'),
            ('SOLD', 'Sold'),
            ('LOST', 'Lost'),
            ('DAMAGED', 'Damaged')
        ],
        default='IN_STOCK'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('RFID', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.RFID}"