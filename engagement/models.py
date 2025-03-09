from django.db import models
from core.models import Unit, City
from core.base_models import BaseEntity
from users.models import CustomUser

# Create your models here.

class UserInteraction(BaseEntity):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('favorite', 'Favorite'),
        ('inquiry', 'Inquiry'),
    ]
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'unit', 'interaction_type'], name='unique_user_unit_interaction'),
            models.UniqueConstraint(fields=['created_by', 'city'], name='unique_user_city_interest'),
        ]

class Notification(BaseEntity):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']