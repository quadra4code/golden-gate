from django.contrib import admin

from users import models

# Register your models here.

admin.site.register([
    models.CustomUser,
    models.UserPhoneNumber
])