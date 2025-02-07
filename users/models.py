from django.db import models
from django.contrib.auth.models import AbstractUser
from core.base_models import BaseEntity
# Create your models here.

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('0', 'Superuser'),
        ('1', 'Manager'),
        ('3', 'Admin'),
        ('4', 'Sales'),
        ('5', 'Buyer'),
        ('6', 'Seller'),
        ('7', 'Broker'),
    ]
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60, null=True, blank=True)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=60, null=True, blank=True, unique=True)
    email_confirmed = models.BooleanField(default=False)
    image_url = models.CharField(max_length=1000, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(max_length=2, default='5')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        main_phone_number = self.userphonenumber_set.filter(is_main_number=True).first()
        return {
            'id': self.id,
            'first_name': f"{self.first_name}",
            'last_name': f"{self.last_name}",
            'username': self.username,
            'main_phone_number': main_phone_number.phone_number.strip() if main_phone_number else None,
            'email': self.email,
            'email_confirmed': self.email_confirmed,
            'date_joined': self.date_joined.strftime('%a %d %b %Y, %H:%M:%S %p') if self.date_joined else None,
            'last_login': self.last_login.strftime('%a %d %b %Y, %H:%M:%S %p') if self.last_login else None,
            'is_superuser': self.is_superuser,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'user_type': self.user_type,
            'user_type_display': self.get_user_type_display(),
            'image_url': self.image_url
        }

class UserPhoneNumber(BaseEntity):
    phone_number = models.CharField(max_length=20, unique=True)
    phone_number_confirmed = models.BooleanField(default=False)
    is_main_number = models.BooleanField(default=False)
    # user = models.ForeignKey(to=CustomUser, on_delete=models.PROTECT) use created_by field instead

    def __str__(self):
        return f"Phone Number: {self.phone_number} | User Full Name: {self.user.first_name} {self.user.last_name}"