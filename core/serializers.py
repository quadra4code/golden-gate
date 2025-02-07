from rest_framework import serializers
from core import models
# Create your serializers here.

class LandSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=3, write_only=True)
    project_type_id = serializers.CharField(max_length=1, write_only=True)
    city_id = serializers.CharField(max_length=2, write_only=True)
    pcp_id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=1000)
    area = serializers.IntegerField()
    price = serializers.DecimalField(decimal_places=4, max_digits=16)
    title = serializers.CharField(max_length=200)
    payment_method = serializers.CharField(max_length=2)
    installment_period = serializers.IntegerField()
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16)
    phone_number = serializers.CharField(max_length=20)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        project_id, project_type_id, city_id = validated_data.pop('project_id'), validated_data.pop('project_type_id'), validated_data.pop('city_id')
        pcp_obj, created = models.PCP.objects.get_or_create(project_id=project_id, project_type_id=project_type_id, city_id=city_id)
        if created:
            pcp_obj.created_by_id = validated_data.get('created_by_id')
            pcp_obj.save()
        validated_data['pcp'] = pcp_obj
        validated_data['status'] = models.Status.objects.filter(code=1).first()# For Sale
        return models.Land.objects.create(**validated_data)

class UnitSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=3, write_only=True)
    project_type_id = serializers.CharField(max_length=1, write_only=True)
    city_id = serializers.CharField(max_length=2, write_only=True)
    pcp_id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=1000)
    area = serializers.IntegerField()
    price = serializers.DecimalField(decimal_places=4, max_digits=16)
    title = serializers.CharField(max_length=200)
    payment_method = serializers.CharField(max_length=2)
    installment_period = serializers.IntegerField()
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16)
    floor = serializers.ChoiceField(choices=['GR', "RP", "LA"])
    phone_number = serializers.CharField(max_length=20)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        project_id, project_type_id, city_id = validated_data.pop('project_id'), validated_data.pop('project_type_id'), validated_data.pop('city_id')
        pcp_obj, created = models.PCP.objects.get_or_create(project_id=project_id, project_type_id=project_type_id, city_id=city_id)
        if created:
            pcp_obj.created_by_id = validated_data.get('created_by_id')
            pcp_obj.save()
        validated_data['pcp'] = pcp_obj
        validated_data['status'] = models.Status.objects.filter(code=1).first()# For Sale
        return models.Unit.objects.create(**validated_data)

class PropertyRequestSerializer(serializers.Serializer):
    property_id = serializers.IntegerField(min_value=1, write_only=True)
    created_by_id = serializers.IntegerField(min_value=1)
    property_type = serializers.ChoiceField(choices=[1, 2], write_only=True)

    def create(self, validated_data):
        property_type = validated_data.pop('property_type')
        if property_type == 1:
            validated_data['land_id'] = validated_data.pop('property_id')
            land_obj = models.Land.objects.filter(id=validated_data.get('land_id')).first()
            if land_obj:
                requested_status = models.Status.objects.filter(code=0).first()# For Requested
                land_obj.status = requested_status
                land_obj.save()
                return models.LandRequest.objects.create(**validated_data)
            else:
                raise LookupError('Land doesn\'t exist')
        elif property_type == 2:
            validated_data['unit_id'] = validated_data.pop('property_id')
            unit_obj = models.Land.objects.filter(id=validated_data.get('unit_id')).first()
            if unit_obj:
                requested_status = models.Status.objects.filter(code=0).first()# For Requested
                unit_obj.status = requested_status
                unit_obj.save()
                return models.UnitRequest.objects.create(**validated_data)
            else:
                raise LookupError('Unit doesn\'t exist')
        else:
            raise LookupError('Invalid Property Type')