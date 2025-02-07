from django.contrib import admin
from core import models
# Register your models here.

admin.site.register([
    models.City,
    models.Project,
    models.ProjectType,
    models.PCP,
    models.Land,
    models.LandRequest,
    models.Unit,
    models.UnitRequest,
    models.UnitImage,
    models.Status,
])