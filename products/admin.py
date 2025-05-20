from django.contrib import admin
from .models import Product, ProductInstance


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode', 'selling_price')
    search_fields = ('name', 'barcode')


@admin.register(ProductInstance)
class ProductInstanceAdmin(admin.ModelAdmin):
    list_display = ('RFID', 'product', 'status')
