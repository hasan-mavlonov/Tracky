from django.db import models
from products.models import ProductInstance


class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class SoldItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product_instance = models.ForeignKey(ProductInstance, on_delete=models.PROTECT)
    sold_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["product_instance"]),
        ]


class Refund(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class RefundedItem(models.Model):
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE, related_name="items")
    sold_item = models.OneToOneField('SoldItem', on_delete=models.PROTECT)
    refunded_at = models.DateTimeField(auto_now_add=True)
