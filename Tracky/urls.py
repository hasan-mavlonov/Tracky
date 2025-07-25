# Tracky/Tracky/urls.py
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.i18n import set_language

from products.sitemaps import StaticViewSitemap, ProductSitemap, ShopSitemap
from products.views import robots_txt
from .views import BaseView, LandingView, LoginView, LogoutView, ForgotPasswordView, APILoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('products/', include('products.urls')),
    path('shops/', include('shops.urls')),
    path('sales/', include('sales.urls')),
    path('users/', include('users.urls')),
    path('set_language/', set_language, name='set_language'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
    path('forgot_password/', ForgotPasswordView, name='forgot_password'),
    path('api/login/', APILoginView.as_view(), name='api-login'),
]

urlpatterns += i18n_patterns(
    path('', LandingView, name='landing_view'),
    path('dashboard/', BaseView, name='base_view'),
)
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'shops': ShopSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
