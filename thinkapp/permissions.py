# 3rd create permissions
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Allows access only to Admin users."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name="admin").exists()

class IsManager(BasePermission):
    """Allows access only to Manager users."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name="manager").exists()

class IsStudent(BasePermission):
    """Allows access only to Student users."""
    def has_permission(self, request, view):
        return request.user.groups.filter(name="student").exists()
