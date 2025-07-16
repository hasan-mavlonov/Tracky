"""
URL configuration for Tracky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.contrib import admin
from django.urls import path, include
from .views import BaseView, LandingView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('shops/', include('shops.urls')),
    path('sales/', include('sales.urls')),
    path('set_language/', set_language, name='set_language'),  # ✅ Add this
]

# i18n URLs (if you're using translation on the landing/dashboard)
urlpatterns += i18n_patterns(
    path('', LandingView, name='landing_view'),
    path('dashboard/', BaseView, name='base_view'),
)
