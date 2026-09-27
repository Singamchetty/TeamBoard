from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    """Allows access only to companies whose role is Company.Role.ADMIN."""

    def has_permission(self, request, view):
        company = getattr(request.user, 'company', None)
        return bool(company and company.role == Company.Role.ADMIN)
