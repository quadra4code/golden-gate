from rest_framework import serializers
from core import models
# Create your serializers here.

class UnitSerializer(serializers.Serializer):
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
    PAYMENT_METHOD_CHOICES = [
        'CS',
        'IN',
    ]
    
    id = serializers.IntegerField(read_only=True)
    unit_type_id = serializers.CharField(max_length=1)
    proposal_id = serializers.CharField(max_length=3)
    project_id = serializers.CharField(max_length=3)
    city_id = serializers.CharField(max_length=2)
    # pcp_id = serializers.IntegerField(read_only=True)
    unit_number = serializers.CharField(max_length=5)
    building_number = serializers.CharField(max_length=150, required=False, allow_null=True)
    area = serializers.IntegerField()
    over_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    total_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    meter_price = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    title = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(max_length=20)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    floor = serializers.ChoiceField(choices=FLOOR_CHOICES, required=False, allow_null=True, allow_blank=True)
    facade = serializers.ChoiceField(choices=FACADE_CHOICES, required=False, allow_null=True, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=False, allow_blank=True, allow_null=True)
    installment_period = serializers.IntegerField(required=False, allow_null=True)
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16, required=False, allow_null=True)
    created_by_id = serializers.IntegerField(min_value=1)

    def is_valid(self, *, raise_exception=False):
        if self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('floor'):
            raise ValueError('الدور يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "2" and not self.initial_data.get('building_number'):
            raise ValueError('رقم العمارة يجب أن يكون موجوداً للوحدات السكنية')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('floor'):
            raise ValueError('الدور لا يجب أن يكون موجوداً للأراضى')
        elif self.initial_data.get('unit_type_id') == "1" and self.initial_data.get('building_number'):
            raise ValueError('رقم العمارة لا يجب أن يكون موجوداً للأراضى')
        elif not any([self.initial_data.get('over_price') or self.initial_data.get('total_price') or self.initial_data.get('meter_price')]):
            raise ValueError("يجب إدخال سعر الأوفر أو إجمالى السعر أو سعر المتر على الأقل")
        elif not models.UnitTypeProject.objects.filter(unit_type_id=self.initial_data.get('unit_type_id'), project_id=self.initial_data.get('project_id')).exists():
            raise ValueError(f'مشروع {models.Project.objects.get(id=self.initial_data.get("project_id")).name} غير متاح لل{models.UnitType.objects.get(id=self.initial_data.get("unit_type_id")).name}')
        return super().is_valid(raise_exception=raise_exception)
    def create(self, validated_data):
        validated_data['status'] = models.Status.objects.filter(code=1).first()# For Sale
        return models.Unit.objects.create(**validated_data)

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


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Consultation
        fields = ['id', 'title', 'body', 'type']

class DrawResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DrawResult
        fields = ['id', 'winner_name', 'property_number', 'building_or_region', 'project_name', 'floor']