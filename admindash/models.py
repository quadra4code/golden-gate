from django.db import models
from core.models import UnitRequest
from users.models import CustomUser
from core.base_models import BaseEntity

# Create your models here.

class SalesRequest(BaseEntity):
    sales = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request = models.OneToOneField(UnitRequest, on_delete=models.CASCADE)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['sales', 'request'], name='sales_request_unique_constraint', violation_error_message='لقد عينت موظف المبيعات إلى هذا الطلب من قبل')
    #     ]