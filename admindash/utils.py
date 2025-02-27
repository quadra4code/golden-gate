from rest_framework.permissions import BasePermission

class IsStaffUser(BasePermission):
    """
    Allows access only to all staff users.
    """

    def has_permission(self, request, view):
        return bool((request.user and request.user.is_staff) or (request.user and request.user.is_superuser))

class IsManagerOrAdminUser(BasePermission):
    """
    Allows access only to manager or admin users.
    """

    def has_permission(self, request, view):
        return bool((request.user and request.user.groups.filter(name='Manager')) or (request.user and request.user.groups.filter(name='Admin')) or (request.user and request.user.is_superuser))

class IsManagerUser(BasePermission):
    """
    Allows access only to manager users.
    """

    def has_permission(self, request, view):
        return bool((request.user and request.user.groups.filter(name='Manager')) or (request.user and request.user.is_superuser))
    

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool((request.user and request.user.groups.filter(name='Admin')) or (request.user and request.user.is_superuser))
    

class IsSalesUser(BasePermission):
    """
    Allows access only to sales users.
    """

    def has_permission(self, request, view):
        return bool((request.user and request.user.groups.filter(name='Sales')) or (request.user and request.user.is_superuser))