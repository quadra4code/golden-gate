from django.contrib import admin

from users.models import UserPhoneNumber

# Register your models here.

admin.site.register([
    UserPhoneNumber
])