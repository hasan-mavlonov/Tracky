from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse

from products.models import Product
from shops.models import Shop


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['landing_view', 'base_view']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.all().order_by("pk")  # Add ordering

    def location(self, obj):
        return reverse('product-detail', args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at


class ShopSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Shop.objects.all().order_by("pk")  # Add ordering

    def location(self, obj):
        return reverse('shop-detail', args=[obj.pk])

    def lastmod(self, obj):
        return obj.updated_at
