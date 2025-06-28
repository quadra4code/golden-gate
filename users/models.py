import uuid
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from core.base_models import BaseEntity
from cloudinary import uploader
from cloudinary.models import CloudinaryField

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
    image = CloudinaryField('image', folder='users_images', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES, default='5')
    referral_code = models.CharField(max_length=12, unique=True, blank=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')  # Who referred this user
    referral_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        main_phone_number = UserPhoneNumber.objects.filter(created_by = self, is_main_number=True).first()
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
            'image_url': self.image,
            'referral_code': self.referral_code,
            'referred_by': self.referred_by.__str__(),
            'referral_count': self.referral_count,
        }
    
    def save(self, *args, **kwargs):
        # Ensure every user has a referral code upon creation
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4().hex[:12])  # Generate a unique 12-character code
        super().save(*args, **kwargs)

@receiver(post_delete, sender=CustomUser)
def delete_user_image_from_cloudinary(sender, instance, **kwargs):
    """
    Signal handler to delete the image from Cloudinary when a CustomUser is deleted.
    """
    uploader.destroy(instance.image.public_id)

class UserPhoneNumber(BaseEntity):
    phone_number = models.CharField(max_length=20, unique=True)
    phone_number_confirmed = models.BooleanField(default=False)
    is_main_number = models.BooleanField(default=False)

    def __str__(self):
        return f"Phone Number: {self.phone_number} | User Full Name: {self.created_by.get_full_name()}"