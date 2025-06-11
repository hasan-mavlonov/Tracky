from django.db import models
from products.models import ProductInstance
from shops.models import Shop


class Sale(models.Model):
    product_instance = models.ForeignKey(ProductInstance, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_instance.product.name} x {self.quantity} at {self.shop}"
