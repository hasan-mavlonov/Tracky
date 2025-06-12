from django.contrib import admin
from .models import Sale, SoldItem, Refund, RefundedItem


class SoldItemInline(admin.TabularInline):
    model = SoldItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [SoldItemInline]


class RefundedItemInline(admin.TabularInline):
    model = RefundedItem
    extra = 0


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [RefundedItemInline]
