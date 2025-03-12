from django.db import models
from core.models import Unit, City
from core.base_models import BaseEntity
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
# Create your models here.

class UserInteraction(BaseEntity):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('favorite', 'Favorite'),
        ('filter', 'Filter'),
        ('register', 'Register'),
    ]
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'unit', 'interaction_type'], name='unique_user_unit_interaction'),
            models.UniqueConstraint(fields=['created_by', 'city', 'interaction_type'], name='unique_user_city_interaction'),
        ]

class Notification(BaseEntity):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    # is_read = models.BooleanField(default=False) # replace with is_deleted

    class Meta:
        ordering = ['-created_at']


@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    """Send real-time notification when a new Notification is created"""
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{instance.created_by.id}",
            {
                "type": "send_notification",
                "message": instance.message,
            },
        )


