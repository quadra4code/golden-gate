import cloudinary.uploader
from django.utils import timezone
from rest_framework import serializers
from core import models
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
    ]
    CURRENCY_CHOICES = ['EGP', 'USD']
    
    id = serializers.IntegerField(required=False, allow_null=True)
    unit_type_id = serializers.CharField(max_length=1)
    proposal_id = serializers.CharField(max_length=3, required=False, allow_null=True)
    project_id = serializers.CharField(max_length=3)
    city_id = serializers.CharField(max_length=2)
    unit_number = serializers.CharField(max_length=5)
    building_number = serializers.CharField(max_length=150, required=False, allow_null=True)
    area = serializers.FloatField()
    paid_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    paid_amount_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    remaining_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    remaining_amount_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    over_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    over_price_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
    total_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    total_price_currency = serializers.ChoiceField(choices=CURRENCY_CHOICES, default='EGP', required=False, allow_null=True)
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
        print(self.initial_data.get('old_images'))
        print(self.initial_data.get('images'))
        if self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('floor'):
            raise ValueError('الدور يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('building_number'):
            raise ValueError('رقم العمارة يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('floor'):
            print(self.initial_data.get('unit_type_id'))
            print(self.initial_data.get('floor'))
            print('condition ', (self.initial_data.get('unit_type_id') == "1") and self.initial_data.get('floor'))
            self.initial_data.pop('floor')
            # raise ValueError('الدور لا يجب أن يكون موجوداً للأراضى')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('building_number'):
            self.initial_data.pop('building_number')
            # raise ValueError('رقم العمارة لا يجب أن يكون موجوداً للأراضى')
        elif not any([self.initial_data.get('over_price') or self.initial_data.get('total_price') or self.initial_data.get('meter_price')]):
            raise ValueError("يجب إدخال سعر الأوفر أو إجمالى السعر أو سعر المتر على الأقل")
        elif not models.UnitTypeProject.objects.filter(unit_type_id=self.initial_data.get('unit_type_id'), project_id=self.initial_data.get('project_id')).exists():
            raise ValueError(f'مشروع {models.Project.objects.get(id=self.initial_data.get("project_id")).name} غير متاح لل{models.UnitType.objects.get(id=self.initial_data.get("unit_type_id")).name}')
        return super().is_valid(raise_exception=raise_exception)

    def create(self, validated_data):
        images = validated_data.pop('images', None)
        is_update = validated_data.pop('update', False)
        
        if not is_update:  # Create new unit
            validated_data['status'] = models.Status.objects.filter(code=1).first()  # For Sale
            unit = models.Unit.objects.create(**validated_data)
        else:  # Update existing unit
            unit_id = validated_data.pop('id', None)
            if not unit_id:
                raise serializers.ValidationError({"id": "ID is required for updating a unit."})

            unit = models.Unit.objects.get(id=unit_id)  # Retrieve existing object
            for key, value in validated_data.items():
                setattr(unit, key, value)  # Update fields
            unit.save()  # Save changes

            # Handle image updates
            old_images = validated_data.pop('old_images', None)
            if old_images is not None:
                for old_img in models.UnitImage.objects.filter(unit_id=unit.id):
                    if old_img.image.url not in old_images:
                        cloudinary.uploader.destroy(old_img.image.public_id)
                        old_img.delete()

        # Handle new images
        if images:
            unit_images = [models.UnitImage(unit=unit, image=img, created_by_id=validated_data['created_by_id']) for img in images]
            models.UnitImage.objects.bulk_create(unit_images)

        return unit
    # def create(self, validated_data):
    #     images = validated_data.pop('images') if validated_data.get('images') else None
    #     if not validated_data['update']:
    #         validated_data['status'] = models.Status.objects.filter(code=1).first()# For Sale
    #         unit = models.Unit.objects.create(**validated_data)
    #     else:
    #         validated_data['status'] = models.Status.objects.filter(id=models.Unit.objects.get(id=validated_data.get('id')).status.id).first()# For Sale
    #         print('updating')
    #         old_images = validated_data.pop('old_images') if validated_data.get('old_images') else None
    #         if old_images:
    #             for old_img in models.UnitImage.objects.filter(unit_id=validated_data['id']):
    #                 print(f'old => {old_img.image.url} vs {old_images}')
    #                 if old_img.image.url in old_images:
    #                     print('it exists in both so no deletion')
    #                 else:
    #                     print('oops! in db not in old list so we delete it from db and server')
    #                     api_call_res = cloudinary.uploader.destroy(old_img.image.public_id)
    #                     print(f'api delete call result => {api_call_res}')
    #                     old_img.delete()
    #         validated_data.pop('update')
    #         unit = models.Unit.objects.update(**validated_data)
    #     if images:
    #             unit_images = [models.UnitImage(unit=unit, image=img, created_by_id=validated_data['created_by_id']) for img in images]
    #             models.UnitImage.objects.bulk_create(unit_images)


class GetAllUnitsSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name")
    unit_type = serializers.CharField(source="unit_type.name")
    project = serializers.CharField(source="project.name")
    price_obj = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.Unit
        fields = ["id", "title", "city", "unit_type", "project", "area", "price_obj", "status", "main_image"]

    def get_main_image(self, obj):
        main_image = obj.unitimage_set.order_by("id").first()
        return main_image.image.url if main_image else None

    def get_price_obj(self, obj):
        price = obj.over_price or obj.total_price or obj.meter_price
        price_type = 'الأوفر' if obj.over_price else 'الإجمالى' if obj.total_price else 'سعر المتر'
        currency = obj.get_over_price_currency_display() if obj.over_price else obj.get_total_price_currency_display() if obj.total_price else obj.get_meter_price_currency_display()
        return {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': currency} if price else None

    def get_status(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code, 'color': obj.status.color} if obj.status else None

class UnitDetailsSerializer(serializers.ModelSerializer):
    unit_type = serializers.CharField(source="unit_type.name")
    proposal = serializers.CharField(source="proposal.name")
    project = serializers.CharField(source="project.name")
    city = serializers.CharField(source="city.name")
    facade = serializers.CharField(source="get_facade_display")
    floor = serializers.CharField(source="get_floor_display")
    latest_date = serializers.SerializerMethodField(read_only=True)
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
        return [{"id": idx, "src": img.image.url} for idx, img in enumerate(obj.unitimage_set.order_by("id"))]

    def get_status(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code} if obj.status else None

    def get_favorite_count(self, obj):
        return obj.unitfavorite_set.count()

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
    proposal_id = serializers.CharField(source='proposal.id')
    project_id = serializers.CharField(source='project.id')
    city_id = serializers.CharField(source='city.id')
    images = serializers.SerializerMethodField(read_only=True)
    # unit_number = serializers.CharField(max_length=5)
    # building_number = serializers.CharField(max_length=150, required=False, allow_null=True)
    # area = serializers.FloatField()
    # paid_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # paid_amount_currency = serializers.CharField(source='paid_amount_currency')
    # remaining_amount = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # remaining_amount_currency = serializers.CharField(source='remaining_amount_currency')
    # over_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # over_price_currency = serializers.CharField(source='over_price_currency')
    # total_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # total_price_currency = serializers.CharField(source='total_price_currency')
    # meter_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # meter_price_currency = serializers.CharField(source='meter_price_currency')
    # title = serializers.CharField(max_length=200, required=False, allow_blank=True, allow_null=True)
    # phone_number = serializers.CharField(max_length=20)
    # description = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    # floor = serializers.CharField(source='floor')
    # facade = serializers.CharField(source='facade')
    # payment_method = serializers.CharField(max_length=150, required=False, allow_null=True)
    # installment_period = serializers.CharField(max_length=150, required=False, allow_null=True)
    # first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    # first_installment_value_currency = serializers.CharField(source='first_installment_value_currency')
    # created_by_id = serializers.IntegerField(min_value=1)
    class Meta:
        model = models.Unit
        fields = [
            'id',
            'unit_type_id',
            'proposal_id',
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
            unit_obj = models.Unit.objects.filter(id=validated_data.get('unit_id')).first()
            if unit_obj:
                requested_status = models.Status.objects.filter(code=0).first()# For Requested
                unit_obj.status = requested_status
                unit_obj.save()
                return models.UnitRequest.objects.create(**validated_data)
            else:
                raise LookupError('الوحدة المطلوبة غير موجودة')

class GetAllRequestsSerializer(serializers.ModelSerializer):
    unit_id = serializers.CharField(source='unit.id', read_only=True)
    unit_title = serializers.CharField(source='unit.title', read_only=True)
    unit_proposal = serializers.CharField(source='unit.proposal.name', read_only=True)
    unit_project = serializers.CharField(source='unit.project.name', read_only=True)
    unit_city = serializers.CharField(source='unit.city.name', read_only=True)
    unit_area = serializers.CharField(source='unit.area', read_only=True)
    price_obj = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.UnitRequest
        fields = ['id', 'unit_id', 'unit_title', 'unit_proposal', 'unit_project', 'unit_city', 'unit_area', 'price_obj', 'created_at']#'status',
    
    def get_price_obj(self, obj):
        price = obj.unit.over_price or obj.unit.total_price or obj.unit.meter_price
        price_type = 'الأوفر' if obj.unit.over_price else 'الإجمالى' if obj.unit.total_price else 'سعر المتر'
        currency = obj.unit.get_over_price_currency_display() if obj.unit.over_price else obj.unit.get_total_price_currency_display() if obj.unit.total_price else obj.unit.get_meter_price_currency_display()
        return {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': currency} if price else None

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_id = serializers.IntegerField(min_value=1, write_only=True)
    class Meta:
        model = models.ClientReview
        fields = ['id', 'rate', 'client_name', 'review', 'created_by_id']

class ArticleSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%b-%Y')
    class Meta:
        model = models.Article
        fields = ['id', 'title', 'body', 'created_at']

class ConsultationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConsultationType
        fields = ['id', 'name', 'brief']

class ConsultationSerializer(serializers.ModelSerializer):
    consultation_type = serializers.CharField(source='consultation_type.name')
    class Meta:
        model = models.Consultation
        fields = ['id', 'title', 'body', 'consultation_type']

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
    price_obj = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField(read_only=True)
    main_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.UnitFavorite
        fields = ['id', 'unit', 'created_by_id', 'unit_id', "title", "city", "unit_type", "project", "area", "price_obj", "status", "main_image"]
    
    def get_main_image(self, obj):
        main_image = obj.unit.unitimage_set.order_by("id").first()
        return main_image.image.url if main_image else None

    def get_price_obj(self, obj):
        price = obj.unit.over_price or obj.unit.total_price or obj.unit.meter_price
        price_type = 'الأوفر' if obj.unit.over_price else 'الإجمالى' if obj.unit.total_price else 'سعر المتر'
        currency = obj.unit.get_over_price_currency_display() if obj.unit.over_price else obj.unit.get_total_price_currency_display() if obj.unit.total_price else obj.unit.get_meter_price_currency_display()
        return {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': currency} if price else None

    def get_status(self, obj):
        return {'id': obj.unit.status.id, 'name': obj.unit.status.name, 'code': obj.unit.status.code, 'color': obj.unit.status.color} if obj.unit.status else None
    
    def create(self, validated_data):
        unit_obj = models.Unit.objects.filter(id=validated_data.get('unit')).first()
        if unit_obj:
            validated_data['unit_id'] = validated_data.pop('unit')
            return models.UnitFavorite.objects.create(**validated_data)
        else:
            raise LookupError('الوحدة المطلوبة غير موجودة')


class StatusSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name")
    value = serializers.CharField(source="id")

    class Meta:
        model = models.Status
        fields = ['id', 'label', 'value', 'color']