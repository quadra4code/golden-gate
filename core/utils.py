# from django.core.cache import cache
# from datetime import datetime, timedelta
# from django.utils import timezone

# Create your utils here.

# def get_active_visitors_count():
#     active_time_window = timezone.now() - timedelta(minutes=5)
#     # Get all keys from Redis
#     user_keys = cache.keys("user:*")
#     session_keys = cache.keys("session:*")
#     all_keys = user_keys + session_keys
#     # Count users active within the time window
#     active_count = 0
#     for key in all_keys:
#         last_activity_str = cache.get(key)
#         if last_activity_str:
#             last_activity = datetime.fromisoformat(last_activity_str)
#             if last_activity >= active_time_window:
#                 active_count += 1
#     return active_count



