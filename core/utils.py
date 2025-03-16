
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils import timezone

# Create your utils here.

def get_active_visitors_count():
    active_time_window = timezone.now() - timedelta(minutes=5)
    
    # Get all keys from Redis
    user_keys = cache.keys("user:*")
    session_keys = cache.keys("session:*")
    all_keys = user_keys + session_keys

    # Count users active within the time window
    active_count = 0
    print(f'active time window => {active_time_window}')
    for key in all_keys:
        last_activity_str = cache.get(key)
        print(f'last activity str => {last_activity_str}')
        if last_activity_str:
            last_activity = datetime.fromisoformat(last_activity_str)
            print(f'last activity => {last_activity}')
            print(f'last activity - active time window=> {last_activity - active_time_window}')
            if last_activity >= active_time_window:
                print('yes last activity is greater than or equa acitve time window')
                active_count += 1
    return active_count