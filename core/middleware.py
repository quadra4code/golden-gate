# middleware.py
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a unique key for the user
        if request.user.is_authenticated:
            user_key = f"user:{request.user.id}"  # Authenticated user
        else:
            user_key = f"session:{request.session.session_key}"  # Non-authenticated user

        # Update the last activity timestamp in Redis
        cache.set(user_key, timezone.now().isoformat())

        return self.get_response(request)