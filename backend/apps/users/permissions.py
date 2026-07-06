from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role == Role.ADMIN


class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role in [
            Role.ADMIN, Role.WAREHOUSE_MANAGER
        ]


class IsTransporter(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role in [
            Role.ADMIN, Role.TRANSPORTER
        ]


class IsSupplier(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role in [
            Role.ADMIN, Role.SUPPLIER
        ]
