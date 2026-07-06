from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Administrator"
    SUPPLIER = "supplier", "Supplier"
    WAREHOUSE_MANAGER = "warehouse_manager", "Warehouse Manager"
    TRANSPORTER = "transporter", "Transporter"
    CUSTOMER = "customer", "Customer"


class User(AbstractUser):
    """Custom user model with role-based access control."""

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"
