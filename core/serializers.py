from rest_framework import serializers
from core import models
# Create your serializers here.

class PropertySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    project_id = serializers.CharField(max_length=3, write_only=True)
    project_type_id = serializers.CharField(max_length=1, write_only=True)
    city_id = serializers.CharField(max_length=2, write_only=True)
    pcp_id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=1000)
    area = serializers.IntegerField()
    price = serializers.DecimalField(decimal_places=4, max_digits=16)
    title = serializers.CharField(max_length=200)
    property_number = serializers.CharField(max_length=5)
    building_or_region = serializers.CharField(max_length=150)
    floor = serializers.ChoiceField(choices=['GR', "RP", "LA"], required=False, allow_null=True, allow_blank=True)
    payment_method = serializers.CharField(max_length=2)
    installment_period = serializers.IntegerField()
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16)
    phone_number = serializers.CharField(max_length=20)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        project_id, project_type_id, city_id = validated_data.pop('project_id'), validated_data.pop('project_type_id'), validated_data.pop('city_id')
        if project_type_id == "2" and not validated_data.get('floor'):
            raise ValueError('Floor is required for units')
        if project_type_id == "1" and validated_data.get('floor'):
            validated_data.pop('floor')
        pcp_obj, created = models.PCP.objects.get_or_create(project_id=project_id, project_type_id=project_type_id, city_id=city_id)
        if created:
            pcp_obj.created_by_id = validated_data.get('created_by_id')
            pcp_obj.save()
        validated_data['pcp'] = pcp_obj
        validated_data['status'] = models.Status.objects.filter(code=1).first()# For Sale
        return models.Property.objects.create(**validated_data)

class PropertyRequestSerializer(serializers.Serializer):
    property_id = serializers.IntegerField(min_value=1, write_only=True)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
            property_obj = models.Property.objects.filter(id=validated_data.get('property_id')).first()
            if property_obj:
                requested_status = models.Status.objects.filter(code=0).first()# For Requested
                property_obj.status = requested_status
                property_obj.save()
                return models.PropertyRequest.objects.create(**validated_data)
            else:
                raise LookupError('Property doesn\'t exist')

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    city_name = serializers.CharField(source='property.pcp.city.name', read_only=True)
    
    class Meta:
        model = models.PropertyClientReview
        fields = ['id', 'rate', 'client_name', 'review', 'city_name']


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
        fields = ['id', 'winner_name', 'property_number', 'building_or_region', 'floor']