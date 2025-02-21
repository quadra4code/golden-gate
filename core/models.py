from django.db import models
from django.forms import ValidationError
from core.base_models import BaseEntity

# Create your models here.
class UnitType(BaseEntity):
    name = models.CharField(max_length=40, unique=True)

class Proposal(BaseEntity):
    name = models.CharField(max_length=255, unique=True)

class Project(BaseEntity):
    name = models.CharField(max_length=50, unique=True)

class UnitTypeProject(BaseEntity):
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

class City(BaseEntity):
    name = models.CharField(max_length=50, unique=True)

class Region(BaseEntity):
    name = models.CharField(max_length=100)
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

class Unit(BaseEntity):
    FACADE_CHOICES = [
        ('0', 'بحرية'),
        ('1', 'قبلية'),
        ('2', 'شرقية'),
        ('3', 'غربية'),
        ('4', 'بحرية شرقية'),
        ('5', 'بحرية غربية'),
        ('6', 'قبلية شرقية'),
        ('7', 'قبلية غربية'),
    ]
    FLOOR_CHOICES = [
        ('0', 'الأرضى'),
        ('1', 'الأول'),
        ('2', 'الثانى'),
        ('3', 'الثالث'),
        ('4', 'الرابع'),
        ('5', 'الخامس'),
        ('6', 'السادس'),
        ('7', 'السابع'),
        ('8', 'الثامن'),
        ('9', 'التاسع'),
        ('10', 'العاشر'),
        ('11', 'الحادى عشر'),
        ('12', 'الثانى عشر'),
        ('13', 'الثالث عشر'),
        ('14', 'الرابع عشر'),
        ('15', 'الخامس عشر'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('CS', 'كاش'),
        ('IN', 'تقسيط'),
    ]
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    unit_number = models.CharField(max_length=20)
    building_number = models.CharField(max_length=150, null=True)
    area = models.FloatField(default=0.0)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=600, null=True, blank=True)
    payment_method = models.CharField(max_length=2, choices=PAYMENT_METHOD_CHOICES, null=True)
    installment_period = models.PositiveIntegerField(null=True)
    first_installment_value = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    over_price = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    total_price = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    meter_price = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)
    facade = models.CharField(max_length=1, choices=FACADE_CHOICES, null=True)
    floor = models.CharField(max_length=2, choices=FLOOR_CHOICES, null=True)
    featured = models.BooleanField(default=False)

    def clean(self):
        """Ensure at least one price field is provided."""
        if not any([self.over_price, self.total_price, self.meter_price]):
            raise ValidationError("يجب إدخال سعر الأوفر أو إجمالى السعر أو سعر المتر على الأقل")

    def save(self, *args, **kwargs):
        """Call the clean method before saving."""
        self.clean()
        super().save(*args, **kwargs)

class UnitImage(BaseEntity):
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='units_images/')

class UnitRequest(BaseEntity):
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'unit'], name='created_by_unit_request_unique_constraint', violation_error_message='لقد طلبت هذه الوحدة من قبل ولا يمكنك طلبها مره أخرى')
        ]

class UnitFavorite(BaseEntity):
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'unit'], name='created_by_unit_favorite_unique_constraint', violation_error_message='لقد أضفت هذه الوحدة للمفضلة من قبل ولا يمكنك إضافتها مره أخرى')
        ]

class ClientReview(BaseEntity):
    rate = models.IntegerField()
    review = models.CharField(max_length=800)
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['created_by', 'property'], name='created_by_property_review_unique_constraint', violation_error_message='Each client car review a property only once')
    #     ]

class Article(BaseEntity):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=2000)

class ConsultationType(BaseEntity):
    name = models.CharField(max_length=100)
    brief = models.CharField(max_length=500, null=True, blank=True)

class Consultation(BaseEntity):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=2000)
    consultation_type = models.ForeignKey(ConsultationType, on_delete=models.CASCADE)

class DrawResult(BaseEntity):
    winner_name = models.CharField(max_length=150)
    search_name = models.CharField(max_length=150, default='---')
    property_number = models.CharField(max_length=50, default='---')
    building_or_region = models.CharField(max_length=150, default='---')
    project_name = models.CharField(max_length=150, default='---')
    floor = models.CharField(max_length=50, default='---')
    area = models.CharField(max_length=50, default='---')

    def __str__(self):
        return f"{self.winner_name} - {self.building_or_region} - {self.property_number} - {self.project_name}{f' - {self.floor}' if self.floor else ''}"

class ContactUs(BaseEntity):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    message = models.CharField(max_length=1000)