from django.db import models
from core.base_models import BaseEntity

# Create your models here.

class City(BaseEntity):
    name = models.CharField(max_length=50, unique=True)

class Project(BaseEntity):
    name = models.CharField(max_length=50, unique=True)

class ProjectType(BaseEntity):
    name = models.CharField(max_length=40, unique=True)

class PCP(BaseEntity): # Project City ProjectType
    project_type = models.ForeignKey(ProjectType, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

class Status(BaseEntity):
    name = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=2, unique=True)
    color = models.CharField(max_length=7, unique=True)
    '''
    Suggested statuses
    0 : تم الطلب : Requested
    1 : للبيع : For Sale
    2 : جارى التفاوض : Under Negotiations
    3 : تم الشراء : Bought
    4 : تم البيع : Sold
    '''

class Property(BaseEntity):
    PAYMENT_METHOD_CHOICES = [
        ('CS', 'كاش'),
        ('IN', 'تقسيط'),
    ]
    pcp = models.ForeignKey(PCP, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    area = models.PositiveIntegerField(default=0)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES, default='CS')
    installment_period = models.IntegerField()
    first_installment_value = models.DecimalField(decimal_places=4, max_digits=16)
    price = models.DecimalField(decimal_places=4, max_digits=16)
    rate = models.IntegerField(default=1)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)
    property_number = models.CharField(max_length=5)
    building_or_region = models.CharField(max_length=150)
    FLOOR_CHOICES = [
        ('GR', 'أرضى'),
        ('RP', 'متكرر'),
        ('LA', 'أخير'),
    ]
    floor = models.CharField(max_length=2, choices=FLOOR_CHOICES, null=True, blank=True)

class PropertyImage(BaseEntity):
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='properties')

class PropertyRequest(BaseEntity):
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'property'], name='created_by_property_request_unique_constraint', violation_error_message='Each client car request a property only once')
        ]

class PropertyClientReview(BaseEntity):
    rate = models.IntegerField()
    review = models.CharField(max_length=800)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'property'], name='created_by_property_review_unique_constraint', violation_error_message='Each client car review a property only once')
        ]

class Article(BaseEntity):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=2000)

class Consultation(BaseEntity):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=2000)
    type = models.CharField(max_length=120)

class DrawResult(BaseEntity):
    FLOOR_CHOICES = Property.FLOOR_CHOICES

    winner_name = models.CharField(max_length=150)
    property_number = models.CharField(max_length=5)
    building_or_region = models.CharField(max_length=150)
    floor = models.CharField(max_length=10, choices=FLOOR_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.winner_name} - {self.building_or_region} - {self.property_number}{f' - {self.floor}' if self.floor else ''}"