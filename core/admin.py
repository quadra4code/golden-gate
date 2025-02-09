from django.contrib import admin
from core import models
# Register your models here.

admin.site.register([
    models.City,
    models.Project,
    models.ProjectType,
    models.PCP,
    models.Property,
    models.PropertyRequest,
    models.PropertyImage,
    models.PropertyClientReview,
    models.Article,
    models.Consultation,
    models.Status,
    models.DrawResult,
])