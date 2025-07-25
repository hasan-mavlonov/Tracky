# Updated models.py
from django.db import models

from shops.models import Shop


class Product(models.Model):
    """Represents a product type with common attributes"""
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, unique=True)
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rfid_count = models.PositiveIntegerField(default=0)  # New field to track how many RFIDs are associated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['barcode']),
        ]

    def has_available_rfid_slots(self):
        return self.rfid_count < self.quantity

    @property
    def has_rfid(self):
        return self.rfid_count > 0

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
        indexes = [
            models.Index(fields=["RFID"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.RFID}"
