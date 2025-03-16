# # middleware.py

from django.utils import timezone
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthAndActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Step 1: Authenticate the user using JWT if not already authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result is not None:
                    request.user, _ = auth_result  # Set request.user
            except AuthenticationFailed:
                print('user is not authenticated')

        # Step 2: Track user activity
        if request.user.is_authenticated and not request.user.is_staff:
            user_key = f"user:{request.user.id}"  # Authenticated user
        elif not request.user.is_authenticated:
            user_key = f"session:{request.session.session_key}"  # Non-authenticated user
        else:
            user_key = None
        # Update the last activity timestamp in Redis if not staff
        if user_key:
            cache.set(user_key, timezone.now().isoformat())

        # Proceed with the request
        return self.get_response(request)
# from django.utils import timezone
# from django.contrib.auth import get_user_model
# from django.core.cache import cache

# User = get_user_model()

# class UpdateLastActivityMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         print(request.user, request.user.is_authenticated, request.user.id, request.user.is_staff, request.user.is_superuser, sep="///")
#         # Generate a unique key for the user
#         if request.user.is_authenticated and not request.user.is_staff:
#             print('yes authenticated and not staff')
#             user_key = f"user:{request.user.id}"  # Authenticated user
#         elif not request.user.is_authenticated:
#             print('not authenticated so session')
#             user_key = f"session:{request.session.session_key}"  # Non-authenticated user
#         else:
#             print('authenticated and staff')

#         # Update the last activity timestamp in Redis
#         print(user_key)
#         cache.set(user_key, timezone.now().isoformat())

#         return self.get_response(request)