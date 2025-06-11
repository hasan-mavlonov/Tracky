from django.contrib import admin
from .models import Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product_instance', 'shop', 'quantity', 'selling_price', 'sold_at']
    list_filter = ['shop', 'sold_at']
