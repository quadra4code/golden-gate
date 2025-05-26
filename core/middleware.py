from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging

# Create your middlewares here.

logger = logging.getLogger(__name__)

class JWTAuthAndActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_ip_update = {}  # In-memory cache for last IP updates

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __call__(self, request):
        try:
            # JWT Authentication
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                try:
                    jwt_auth = JWTAuthentication()
                    auth_result = jwt_auth.authenticate(request)
                    if auth_result is not None:
                        request.user, _ = auth_result
                except AuthenticationFailed as e:  # Fixed exception variable
                    logger.warning(f"JWT authentication failed: {e}")

            # Activity Tracking
            user_key = None
            current_time = timezone.now().timestamp()
            
            if request.user.is_authenticated:
                if not request.user.is_staff:  # Only if you really want to exclude staff
                    user_key = f"user:{request.user.id}"
            else:
                ip = self.get_client_ip(request)
                # More frequent updates for IPs (5 seconds instead of 10)
                if ip not in self.last_ip_update or (current_time - self.last_ip_update[ip]) >= 5:
                    user_key = f"ip:{ip}"
                    self.last_ip_update[ip] = current_time

            if user_key:
                try:
                    redis_client = get_redis_connection('default')
                    with redis_client.pipeline() as pipe:
                        # Remove entries older than 1 hour
                        pipe.zremrangebyscore("active_visitors", 0, current_time - 3600)
                        # Add/update current user
                        pipe.zadd("active_visitors", {user_key: current_time})
                        # Refresh TTL
                        pipe.expire("active_visitors", 3600)
                        pipe.execute()
                except Exception as e:
                    logger.error(f"Redis operation failed: {e}")

        except Exception as e:
            logger.error(f"Error in middleware: {e}", exc_info=True)
        
        return self.get_response(request)

