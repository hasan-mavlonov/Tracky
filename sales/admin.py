from django.contrib import admin
from .models import Sale, SoldItem


class SoldItemInline(admin.TabularInline):
    model = SoldItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [SoldItemInline]
