from django.contrib import admin
from core.models import City, Project, ProjectType, PCP, Land, Unit, Status
# Register your models here.

admin.site.register([
    City,
    Project,
    ProjectType,
    PCP,
    Land,
    Unit,
    Status
])