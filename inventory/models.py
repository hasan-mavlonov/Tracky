from django.db import models
from shops.models import Shop
from products.models import Product


class ProductInstance(models.Model):
    STATUS_CHOICES = [
        ('IN_STOCK', 'In Stock'),
        ('SOLD', 'Sold'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rfid = models.CharField(max_length=100, unique=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='IN_STOCK'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rfid}"


class ShopInventory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('shop', 'product')

    def __str__(self):
        return f"{self.shop.name} - {self.product.name} ({self.stock_quantity})"


