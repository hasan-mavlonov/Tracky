from django.db import models
from products.models import ProductInstance


class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class SoldItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product_instance = models.OneToOneField(ProductInstance, on_delete=models.PROTECT)
    sold_at = models.DateTimeField(auto_now_add=True)
