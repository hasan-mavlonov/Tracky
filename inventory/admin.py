from django.contrib import admin
from .models import ProductInstance, ShopInventory

@admin.register(ProductInstance)
class ProductInstanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'rfid', 'shop', 'status')
    list_filter = ('status', 'shop')

@admin.register(ShopInventory)
class ShopInventoryAdmin(admin.ModelAdmin):
    list_display = ('shop', 'product', 'stock_quantity')