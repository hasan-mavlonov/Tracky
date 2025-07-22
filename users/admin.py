from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['phone_number', 'first_name', 'last_name', 'role', 'shop', 'is_active', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active', 'shop']
    search_fields = ['phone_number', 'first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'shop')}),
        (_('Permissions'), {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'password1', 'password2',
                'first_name', 'last_name', 'shop', 'role',
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
            ),
        }),
    )

    # Set the model field used for login
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
