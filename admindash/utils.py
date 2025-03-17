from rest_framework.permissions import BasePermission
from django_redis import get_redis_connection
from django.utils import timezone
import logging

# Create your utils here.

logger = logging.getLogger(__name__)

# region Permissions
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
# endregion

def get_active_visitors_count():
    try:
        # Get the Redis connection
        redis_client = get_redis_connection("default")
        # Define the time window for active users (e.g., last 5 minutes)
        active_time_window = timezone.now().timestamp() - 300  # 5 minutes ago
        # Use the Redis client to call zcount
        active_count = redis_client.zcount("active_visitors", active_time_window, "+inf")
        return active_count
    except Exception as e:
        logger.error(f"Error getting active visitors count: {e}")
        return 0
