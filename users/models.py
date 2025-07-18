from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from shops.models import Shop

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superuser')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('role') != 'superuser':
            raise ValueError('Superuser must have role=superuser.')

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('superuser', 'Superuser'),
        ('tracky_admin', 'Tracky Admin'),
        ('store_admin', 'Store Admin'),
        ('manager', 'Manager'),
        ('seller', 'Seller'),
        ('cashier', 'Cashier'),
    )

    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seller')
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone_number} ({self.get_role_display()})"

    def can_create_users(self):
        return self.role in ['superuser', 'tracky_admin', 'store_admin']

    def allowed_roles_to_create(self):
        if self.role == 'superuser':
            return ['tracky_admin']
        elif self.role == 'tracky_admin':
            return ['store_admin']
        elif self.role == 'store_admin':
            return ['manager', 'seller', 'cashier']
        return []

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['shop']),
        ]