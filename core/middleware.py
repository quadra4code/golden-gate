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

    def __call__(self, request):
        try:
            # Step 1: Authenticate the user using JWT if not already authenticated
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                try:
                    jwt_auth = JWTAuthentication()
                    auth_result = jwt_auth.authenticate(request)
                    if auth_result is not None:
                        request.user, _ = auth_result  # Set request.user
                except AuthenticationFailed:
                    logger.warning(f"JWT authentication failed: {e}")
            # Step 2: Track user activity
            user_key = None
            if request.user.is_authenticated and not request.user.is_staff:
                user_key = f"user:{request.user.id}"  # Authenticated non-staff user
            elif not request.user.is_authenticated:
                if not request.session.session_key:
                    request.session.modified = True  # Mark the session as modified
                    request.session.save()  # Save the session to generate a session key
                user_key = f"session:{request.session.session_key}"  # Non-authenticated user
            # Update the last activity timestamp in Redis if not staff
            if user_key:
                timestamp = timezone.now().timestamp()
                redis_client = get_redis_connection('default')
                with redis_client.pipeline() as pipe:
                    pipe.zadd("active_visitors", {user_key: timestamp})
                    pipe.expire("active_visitors", 3600)  # Set expiry for the sorted set after one hour
                    pipe.execute()
        except Exception as e:
            logger.error(f"Error in JWTAuthAndActivityMiddleware: {e}")
        finally:
            # Proceed with the request
            return self.get_response(request)




