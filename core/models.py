from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.forms import ValidationError
from core.base_models import BaseEntity
from users.models import CustomUser
from cloudinary.models import CloudinaryField
from cloudinary import uploader

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
    3 : تم البيع : Sold
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
        ('16', 'متكرر'),
        ('17', 'الأخير'),
    ]
    CURRENCY_CHOICES = [
        ('EGP', 'جنيه مصرى'),
        ('USD', 'دولار'),
    ]
    unit_type = models.ForeignKey(UnitType, on_delete=models.PROTECT)
    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, null=True)
    proposal_str = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, null=True)
    unit_number = models.CharField(max_length=20)
    building_number = models.CharField(max_length=150, null=True)
    area = models.FloatField(default=0.0)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=600, null=True, blank=True)
    payment_method = models.CharField(max_length=150, null=True, blank=True)
    installment_period = models.CharField(max_length=150, null=True, blank=True)
    first_installment_value = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    first_installment_value_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP', null=True)
    paid_amount = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    paid_amount_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP', null=True)
    remaining_amount = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    remaining_amount_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP', null=True)
    over_price = models.DecimalField(decimal_places=4, max_digits=16)
    over_price_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP')
    total_price = models.DecimalField(decimal_places=4, max_digits=16)
    total_price_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP')
    meter_price = models.DecimalField(decimal_places=4, max_digits=16, null=True)
    meter_price_currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='EGP', null=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    phone_number = models.CharField(max_length=20)
    facade = models.CharField(max_length=1, choices=FACADE_CHOICES, null=True)
    floor = models.CharField(max_length=2, choices=FLOOR_CHOICES, null=True)
    featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(null=True, default=None)
    approver_message = models.CharField(max_length=400, null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['id']

    def clean(self):
        """Ensure at least one price field is provided."""
        if not any([self.over_price, self.total_price, self.meter_price]):
            raise ValidationError("يجب إدخال سعر الأوفر أو إجمالى السعر أو سعر المتر على الأقل")

    def save(self, *args, **kwargs):
        """Call the clean method before saving."""
        self.clean()
        price_fields = [
            ('first_installment_value', 'first_installment_value_currency'),
            ('paid_amount', 'paid_amount_currency'),
            ('remaining_amount', 'remaining_amount_currency'),
            ('over_price', 'over_price_currency'),
            ('total_price', 'total_price_currency'),
            ('meter_price', 'meter_price_currency'),
        ]
        for price_field, currency_field in price_fields:
            if getattr(self, price_field) is None:
                setattr(self, currency_field, None)
            elif getattr(self, currency_field) is None:
                setattr(self, currency_field, "EGP")
        super().save(*args, **kwargs)

class UnitImage(BaseEntity):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    image = CloudinaryField('image', folder='units_images')
    # image = models.ImageField(upload_to='units_images/')

@receiver(post_delete, sender=UnitImage)
def delete_unit_image_from_cloudinary(sender, instance, **kwargs):
    """
    Signal handler to delete the image from Cloudinary when a UnitImage is deleted.
    """
    uploader.destroy(instance.image.public_id)

class UnitRequest(BaseEntity):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, default='0')
    status_msg = models.CharField(max_length=400, blank=True, null=True)
    sales_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_staff_requests')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['created_by', 'unit'], name='created_by_unit_request_unique_constraint', violation_error_message='لقد طلبت هذه الوحدة من قبل ولا يمكنك طلبها مره أخرى')
        ]
        ordering = ['id']

class ClientReview(BaseEntity):
    rate = models.IntegerField()
    review = models.CharField(max_length=800)
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['created_by', 'property'], name='created_by_property_review_unique_constraint', violation_error_message='Each client car review a property only once')
    #     ]

class Article(BaseEntity):
    title = models.CharField(max_length=400)
    body = models.CharField(max_length=5000)
    is_main = models.BooleanField(default=False)
    image = CloudinaryField('image', folder='articles_images', null=True, blank=True)
    class Meta:
        ordering = ['id']

@receiver(post_delete, sender=Article)
def delete_article_image_from_cloudinary(sender, instance, **kwargs):
    """
    Signal handler to delete the image from Cloudinary when a Article is deleted.
    """
    uploader.destroy(instance.image.public_id)

class ConsultationType(BaseEntity):
    name = models.CharField(max_length=100)
    brief = models.CharField(max_length=500, null=True, blank=True)
    class Meta:
        ordering = ['id']

class Consultation(BaseEntity):
    title = models.CharField(max_length=250)
    body = models.CharField(max_length=2000)
    consultation_type = models.ForeignKey(ConsultationType, on_delete=models.CASCADE)
    class Meta:
        ordering = ['id']

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
    class Meta:
        ordering = ['id']