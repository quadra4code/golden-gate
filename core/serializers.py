import cloudinary.uploader
from django.utils import timezone
from rest_framework import serializers
from core import models
from core.constants import REQUEST_STATUS_CHOICES
from engagement.models import UserInteraction
from users.models import CustomUser
# Create your serializers here.

class CreateUnitSerializer(serializers.Serializer):
    FACADE_CHOICES = [
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
    ]
    FLOOR_CHOICES = [
        '0',
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        '11',
        '12',
        '13',
        '14',
        '15',
        '16',
        '17',
    ]
    CURRENCY_CHOICES = ['EGP', 'USD']
    
    id = serializers.IntegerField(required=False, allow_null=True)
    unit_type_id = serializers.CharField(max_length=1)
    proposal_id = serializers.CharField(max_length=3, required=False, allow_null=True)
    proposal_str = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    project_id = serializers.CharField(max_length=3)
    city_id = serializers.CharField(max_length=2)
    unit_number = serializers.CharField(max_length=5)
    building_number = serializers.CharField(max_length=150, required=False, allow_null=True)
    area = serializers.FloatField()
    paid_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    paid_amount_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    remaining_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    remaining_amount_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    over_price = serializers.DecimalField(decimal_places=4, max_digits=16)
    over_price_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP')
    total_price = serializers.DecimalField(decimal_places=4, max_digits=16)
    total_price_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP')
    meter_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    meter_price_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    title = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    floor = serializers.ChoiceField(choices=FLOOR_CHOICES, required=False, allow_null=True, allow_blank=True)
    facade = serializers.ChoiceField(choices=FACADE_CHOICES, required=False, allow_null=True, allow_blank=True)
    payment_method = serializers.CharField(max_length=150, required=False, allow_null=True)
    installment_period = serializers.CharField(max_length=150, required=False, allow_null=True)
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    first_installment_value_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    created_by_id = serializers.IntegerField(min_value=1)
    update = serializers.BooleanField(default=False)
    images = serializers.ListField(required=False, allow_null=True)
    old_images = serializers.ListField(required=False, allow_null=True)

    def is_valid(self, *, raise_exception=False):
        if self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('floor'):
            raise ValueError('الدور يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('building_number'):
            raise ValueError('رقم العمارة يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('floor'):
            raise ValueError('الدور لا يجب أن يكون موجوداً للأراضى')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('building_number'):
            raise ValueError('رقم العمارة لا يجب أن يكون موجوداً للأراضى')
        elif not models.UnitTypeProject.objects.filter(unit_type_id=self.initial_data.get('unit_type_id'), project_id=self.initial_data.get('project_id')).exists():
            raise ValueError(f'مشروع {models.Project.objects.get(id=self.initial_data.get("project_id")).name} غير متاح لل{models.UnitType.objects.get(id=self.initial_data.get("unit_type_id")).name}')
        elif not (self.initial_data.get('images') or self.initial_data.get('update')):
            raise ValueError('يجب إضافة صورة واحدة على الأقل عند إضافة وحدة جديدة')
        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        is_update = validated_data.pop('update', False)
        if not is_update:  # Create new unit
            validated_data['status'] = models.Status.objects.filter(code=1).first()  # For Sale
            # validated_data['is_approved'] = False
            # validated_data['is_deleted'] = True
            unit = models.Unit.objects.create(**validated_data)
        else:  # Update existing unit
            unit_id = validated_data.pop('id', None)
            if not unit_id:
                raise serializers.ValidationError({"id": "ID is required for updating a unit."})

            user_obj = CustomUser.objects.get(id=validated_data['created_by_id'])
            if user_obj.is_staff and user_obj.groups.filter(name__in=['Manager', 'Admin']):
                unit = models.Unit.objects.get(id=unit_id)
            else:
                unit = models.Unit.objects.get(id=unit_id, created_by=user_obj)
            for key, value in validated_data.items():
                setattr(unit, key, value)
            unit.is_approved = None if unit.is_approved == False else unit.is_approved  # Reset approval status if it was False to request another review
            unit.save()
            # Handle image updates
            old_images = validated_data.pop('old_images', None)
            if old_images is not None:
                for existing_img in models.UnitImage.objects.filter(unit_id=unit.id):
                    if existing_img.image.url not in old_images:
                        existing_img.delete()

            elif old_images is None:
                for existing_img in models.UnitImage.objects.filter(unit_id=unit.id):
                    existing_img.delete()

        # Handle new images
        if images:
            unit_images = [models.UnitImage(unit=unit, image=img, created_by_id=validated_data['created_by_id']) for img in images]
            models.UnitImage.objects.bulk_create(unit_images)

        return unit

class GetAllUnitsSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name")
    unit_type = serializers.CharField(source="unit_type.name")
    floor = serializers.CharField(source="get_floor_display")
    project = serializers.CharField(source="project.name")
    over_price_obj = serializers.SerializerMethodField()
    total_price_obj = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    approver_message = serializers.SerializerMethodField()
    class Meta:
        model = models.Unit
        fields = ["id", "title", "city", "unit_type", "proposal_str", "project", "unit_number", "building_number", "floor", "area", "over_price_obj", "total_price_obj", "status", "main_image", "is_approved", "approver_message"]

    def get_main_image(self, obj):
        main_image = obj.unitimage_set.order_by("id").first()
        return main_image.image.url if main_image else None

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.over_price:,.0f}', 'currency': obj.get_over_price_currency_display()} if obj.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.total_price:,.0f}', 'currency': obj.get_total_price_currency_display()} if obj.total_price else None

    def get_status(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code, 'color': obj.status.color} if obj.status else None

    def get_approver_message(self, obj):
        return 'تم قبول الوحدة' if obj.is_approved else 'في انتظار المراجعة' if obj.is_approved is None else obj.approver_message 

class UnitDetailsSerializer(serializers.ModelSerializer):
    unit_type = serializers.CharField(source="unit_type.name")
    proposal = serializers.CharField(source="proposal.name")
    project = serializers.CharField(source="project.name")
    city = serializers.CharField(source="city.name")
    facade = serializers.CharField(source="get_facade_display")
    floor = serializers.CharField(source="get_floor_display")
    latest_date = serializers.SerializerMethodField(read_only=True)
    paid_amount_currency = serializers.CharField(source="get_paid_amount_currency_display", read_only=True)
    remaining_amount_currency = serializers.CharField(source="get_remaining_amount_currency_display", read_only=True)
    over_price_currency = serializers.CharField(source="get_over_price_currency_display", read_only=True)
    total_price_currency = serializers.CharField(source="get_total_price_currency_display", read_only=True)
    meter_price_currency = serializers.CharField(source="get_meter_price_currency_display", read_only=True)
    first_installment_value_currency = serializers.CharField(source="get_first_installment_value_currency_display", read_only=True)
    favorite_count = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.Unit
        fields = [
            "id",
            "title",
            "unit_type",
            "proposal",
            "proposal_str",
            "project",
            "city",
            "area",
            "paid_amount",
            "paid_amount_currency",
            "remaining_amount",
            "remaining_amount_currency",
            "over_price",
            "over_price_currency",
            "total_price",
            "total_price_currency",
            "meter_price",
            "meter_price_currency",
            "latest_date",
            "favorite_count",
            "status",
            "description",
            "floor",
            "facade",
            "payment_method",
            "first_installment_value",
            "first_installment_value_currency",
            "installment_period",
            "images"
        ]

    def get_images(self, obj):
        return [{"id": idx+1, "src": img.image.url} for idx, img in enumerate(obj.unitimage_set.order_by("id"))]

    def get_status(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code} if obj.status else None

    def get_favorite_count(self, obj):
        return obj.userinteraction_set.filter(interaction_type='favorite').count()

    def get_latest_date(self, obj):
        return timezone.localdate(obj.updated_at) if obj.updated_at and (obj.updated_at >= obj.created_at) else timezone.localdate(obj.created_at) if obj.created_at else None

    def to_representation(self, instance):
        """Format price fields as '1,234,567' (no decimal places)."""
        data = super().to_representation(instance)
        price_fields = [
            "paid_amount",
            "remaining_amount",
            "over_price",
            "total_price",
            "meter_price",
            "first_installment_value",
        ]
        for field in price_fields:
            if data.get(field) is not None:
                value = getattr(instance, field, None)
                data[field] = f"{value:,.0f}"
        return data

class UpdateUnitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    unit_type_id = serializers.CharField(max_length=1)
    # proposal_id = serializers.CharField(source='proposal.id')
    project_id = serializers.CharField(source='project.id')
    city_id = serializers.CharField(source='city.id')
    images = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Unit
        fields = [
            'id',
            'unit_type_id',
            # 'proposal_id',
            'proposal_str',
            'project_id',
            'city_id',
            'unit_number',
            'building_number',
            'area',
            'paid_amount',
            'paid_amount_currency',
            'remaining_amount',
            'remaining_amount_currency',
            'over_price',
            'over_price_currency',
            'total_price',
            'total_price_currency',
            'meter_price',
            'meter_price_currency',
            'title',
            'phone_number',
            'description',
            'floor',
            'facade',
            'payment_method',
            'installment_period',
            'first_installment_value',
            'first_installment_value_currency',
            'images'
        ]

    def get_images(self, obj):
        return [img.image.url for img in obj.unitimage_set.order_by("id")]

class UnitRequestSerializer(serializers.Serializer):
    unit_id = serializers.IntegerField(min_value=1, write_only=True)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
            unit_obj = models.Unit.objects.filter(id=validated_data.get('unit_id'), is_deleted=False, is_approved=True).first()
            if unit_obj:
                requested_status = models.Status.objects.filter(code=0).first()# For Requested
                unit_obj.status = requested_status
                unit_obj.save()
                return models.UnitRequest.objects.create(**validated_data)
            else:
                raise LookupError('هذه الوحدة غير متاحة للطلب حالياً')
                # raise LookupError('الوحدة المطلوبة غير موجودة')

class GetAllRequestsSerializer(serializers.ModelSerializer):
    unit_id = serializers.CharField(source='unit.id', read_only=True)
    unit_type = serializers.CharField(source='unit.unit_type.name', read_only=True)
    unit_title = serializers.CharField(source='unit.title', read_only=True)
    unit_proposal = serializers.CharField(source='unit.proposal.name', read_only=True)
    unit_proposal_str = serializers.CharField(source='unit.proposal_str', read_only=True)
    unit_project = serializers.CharField(source='unit.project.name', read_only=True)
    unit_city = serializers.CharField(source='unit.city.name', read_only=True)
    unit_area = serializers.CharField(source='unit.area', read_only=True)
    over_price_obj = serializers.SerializerMethodField(read_only=True)
    total_price_obj = serializers.SerializerMethodField(read_only=True)
    request_status_obj = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)

    class Meta:
        model = models.UnitRequest
        fields = ['id', 'unit_id', 'unit_type', 'unit_title', 'unit_proposal', 'unit_proposal_str', 'unit_project', 'unit_city', 'unit_area', 'over_price_obj', 'total_price_obj', 'request_status_obj', 'created_at', 'updated_at']
    
    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.unit.over_price:,.0f}', 'currency': obj.unit.get_over_price_currency_display()} if obj.unit.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.unit.total_price:,.0f}', 'currency': obj.unit.get_total_price_currency_display()} if obj.unit.total_price else None

    def get_request_status_obj(self, obj):
        status_obj = REQUEST_STATUS_CHOICES.get(obj.status)
        return {'name': status_obj.get('name'), 'color': status_obj.get('color'), 'status_msg': obj.status_msg}

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_id = serializers.IntegerField(min_value=1, write_only=True)
    image_url = serializers.CharField(source='created_by.image.url', read_only=True)
    is_deleted = serializers.BooleanField(write_only=True)

    class Meta:
        model = models.ClientReview
        fields = ['id', 'rate', 'client_name', 'review', 'created_by_id', 'image_url', 'is_deleted']

class ArticleSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%b-%Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    updated_by_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    image_url = serializers.CharField(source='image.url', read_only=True)
    is_main = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Article
        fields = ['id', 'title', 'body', 'image_url', 'image', 'created_by_name', 'updated_by_name',
            'is_main', 'created_by_id', 'created_at', 'updated_by_id', 'updated_at', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None

    def update(self, instance, validated_data):
        new_image = validated_data.get('image', None)
        if new_image and instance.image:
            # Delete the old image from Cloudinary
            public_id = instance.image.public_id if hasattr(instance.image, 'public_id') else None
            if public_id:
                cloudinary.uploader.destroy(public_id)
        return super().update(instance, validated_data)

class ConsultationTypeSerializer(serializers.ModelSerializer):
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    created_by_obj = serializers.SerializerMethodField(read_only=True)
    updated_by_obj = serializers.SerializerMethodField(read_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    created_at = serializers.DateTimeField(format='Date: %d-%m-%Y | Time: %I:%M:%S-%p', read_only=True)
    updated_at = serializers.DateTimeField(format='Date: %d-%m-%Y | Time: %I:%M:%S-%p', read_only=True)

    class Meta:
        model = models.ConsultationType
        fields = ['id', 'name', 'brief', 'created_by_id', 'created_by_obj', 'updated_by_id', 'updated_by_obj', 'created_at', 'updated_at', 'hidden']
    
    def get_created_by_obj(self, obj):
        if obj.created_by:
            return {'id': obj.created_by.id, 'full_name': obj.created_by.get_full_name()}
    def get_updated_by_obj(self, obj):
        if obj.updated_by:
            return {'id': obj.updated_by.id, 'full_name': obj.updated_by.get_full_name()}

class ConsultationSerializer(serializers.ModelSerializer):
    consultation_type = serializers.CharField(source='consultation_type.name', read_only=True)
    consultation_type_id = serializers.CharField(required=False)
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    created_by_obj = serializers.SerializerMethodField(read_only=True)
    updated_by_obj = serializers.SerializerMethodField(read_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    created_at = serializers.DateTimeField(format='Date: %d-%m-%Y | Time: %I:%M:%S-%p', read_only=True)
    updated_at = serializers.DateTimeField(format='Date: %d-%m-%Y | Time: %I:%M:%S-%p', read_only=True)

    class Meta:
        model = models.Consultation
        fields = [
            'id',
            'title',
            'body',
            'consultation_type',
            'consultation_type_id',
            'created_by_id',
            'created_by_obj',
            'updated_by_id',
            'updated_by_obj',
            'created_at',
            'updated_at',
            'hidden',
        ]

    def get_created_by_obj(self, obj):
        if obj.created_by:
            return {'id': obj.created_by.id, 'full_name': obj.created_by.get_full_name()}
    def get_updated_by_obj(self, obj):
        if obj.updated_by:
            return {'id': obj.updated_by.id, 'full_name': obj.updated_by.get_full_name()}

class DrawResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DrawResult
        fields = ['id', 'winner_name', 'property_number', 'building_or_region', 'project_name', 'floor']

class ContactUsSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format='%d-%b-%Y', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%b-%Y', read_only=True)
    class Meta:
        model = models.ContactUs
        fields = ['id', 'name', 'email', 'phone_number', 'message', 'created_at', 'updated_at', 'status']
    
    def get_status(self, obj):
        return {'id': obj.id, 'name': 'تم الحل' if obj.is_deleted else 'قائمة', 'code': 1 if obj.is_deleted else 0}

class UnitFavoriteSerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(min_value=1, write_only=True)
    unit = serializers.IntegerField(min_value=1, write_only=True)
    unit_id = serializers.IntegerField(source='unit.id', read_only=True)
    title = serializers.CharField(source='unit.title', read_only=True)
    city = serializers.CharField(source='unit.city.name', read_only=True)
    unit_type = serializers.CharField(source='unit.unit_type.name', read_only=True)
    project = serializers.CharField(source='unit.project.name', read_only=True)
    area = serializers.FloatField(source='unit.area', read_only=True)
    over_price_obj = serializers.SerializerMethodField(read_only=True)
    total_price_obj = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    main_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserInteraction
        fields = ['id', 'unit', 'created_by_id', 'unit_id', "title", "city", "unit_type", "project", "area", "over_price_obj", "total_price_obj", "status", "main_image"]
    
    def get_main_image(self, obj):
        main_image = obj.unit.unitimage_set.order_by("id").first()
        return main_image.image.url if main_image else None

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.unit.over_price:,.0f}', 'currency': obj.unit.get_over_price_currency_display()} if obj.unit.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.unit.total_price:,.0f}', 'currency': obj.unit.get_total_price_currency_display()} if obj.unit.total_price else None

    def get_status(self, obj):
        return {'id': obj.unit.status.id, 'name': obj.unit.status.name, 'code': obj.unit.status.code, 'color': obj.unit.status.color} if obj.unit.status else None
    
    def create(self, validated_data):
        unit_obj = models.Unit.objects.filter(id=validated_data.get('unit'), is_delete=False, is_approved=True).first()
        if unit_obj:
            validated_data['unit_id'] = validated_data.pop('unit')
            validated_data['interaction_type'] = 'favorite'
            return UserInteraction.objects.create(**validated_data)
        else:
            raise LookupError('هذه الوحدة غير متاحة للمفضلة حالياً')
            # raise LookupError('الوحدة المطلوبة غير موجودة')

class StatusSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")
    value = serializers.CharField(source="id")

    class Meta:
        model = models.Status
        fields = ['id', 'label', 'value', 'color']







