from django.urls import path
from engagement import views

# Create your urls here.

urlpatterns = [
    path('all-notifications', views.all_notifications_view, name='all_notifications'),
    path('mark-read/<int:notification_id>', views.mark_read_view, name='mark_read'),
    path('mark-all-read', views.mark_all_read_view, name='mark_all_read_view'),
    path('delete/<str:flag>', views.delete_notification_view, name='delete_notification_view'),
]