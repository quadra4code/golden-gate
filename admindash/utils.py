from rest_framework.permissions import BasePermission

class CustomBasePermission(BasePermission):
    """
    Allows access to superuser
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsStaffUser(BasePermission):
    """
    Allows access only to all staff users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

class IsManagerUser(BasePermission):
    """
    Allows access only to manager users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Manager'))
    

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Admin'))
    

class IsSalesUser(BasePermission):
    """
    Allows access only to sales users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Sales'))