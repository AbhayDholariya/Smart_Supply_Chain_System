from django.db import models


class Warehouse(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(help_text="Maximum storage units")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, default="unit")
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sku} — {self.name}"


class InventoryItem(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventory")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory")
    quantity = models.PositiveIntegerField(default=0)
    reorder_threshold = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("warehouse", "product")

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.reorder_threshold

    def __str__(self) -> str:
        return f"{self.product.sku} @ {self.warehouse.name}: {self.quantity}"
