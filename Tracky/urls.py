from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.contrib import admin
from django.urls import path, include
from .views import BaseView, LandingView, LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('shops/', include('shops.urls')),
    path('sales/', include('sales.urls')),
    path('set_language/', set_language, name='set_language'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
]

urlpatterns += i18n_patterns(
    path('', LandingView, name='landing_view'),
    path('dashboard/', BaseView, name='base_view'),
)
