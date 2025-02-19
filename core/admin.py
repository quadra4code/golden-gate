from django.contrib import admin
from core import models
# Register your models here.

admin.site.register([
    models.UnitType,
    models.Proposal,
    models.Project,
    models.UnitTypeProject,
    models.City,
    models.Region,
    models.Unit,
    models.UnitRequest,
    models.UnitImage,
    models.ClientReview,
    models.Article,
    models.Consultation,
    models.Status,
    models.DrawResult,
    models.ContactUs,
])