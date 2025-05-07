from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100)
    RFID = models.CharField(max_length=100, null=True, blank=True)
    bought_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['barcode']),
        ]

    def __str__(self):
        return f"{self.name} (${self.selling_price})"
