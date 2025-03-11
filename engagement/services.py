from core.base_models import ResultView
from engagement import models
from engagement import serializers

# Create your services here.

def all_notifications_service(user_obj):
    result = ResultView()
    try:
        notifications = models.Notification.objects.filter(created_by=user_obj)
        serialized_notifications = serializers.NotificationSerializer(notifications, many=True)
        result.msg = 'تم جلب الإشعارات بنجاح'
        result.data = serialized_notifications.data
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الإشعارات'
        result.data = {'errors': str(e)}
    finally:
        return result

def mark_read_service(user_obj, notification_id):
    result = ResultView()
    try:
        notification = models.Notification.objects.get(notification_id=notification_id)
        notification.is_deleted = True
        # serialized_notifications = serializers.NotificationSerializer(notifications, many=True)
        result.msg = 'تم تعليم الإشعار كمقروء بنجاح'
        # result.data = serialized_notifications.data
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تعليم الإشعار كمقروء'
        result.data = {'errors': str(e)}
    finally:
        return result

def mark_all_read_service(user_obj):
    result = ResultView()
    try:
        notifications = models.Notification.objects.filter(created_by=user_obj, is_deleted=False).update(is_delete=True)
        serialized_notifications = serializers.NotificationSerializer(notifications, many=True)
        result.msg = 'تم تعليم كل الإشعارات كمقروءة بنجاح'
        result.data = serialized_notifications.data
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تعليم كل الإشعارات كمقروءة'
        result.data = {'errors': str(e)}
    finally:
        return result