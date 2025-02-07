from rest_framework import serializers
from core.models import Land, PCP, Status
# Create your serializers here.

class LandSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=3, write_only=True)
    project_type_id = serializers.CharField(max_length=1, write_only=True)
    city_id = serializers.CharField(max_length=2, write_only=True)
    pcp_id = serializers.IntegerField(read_only=True)
    description = serializers.CharField(max_length=1000)
    area = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=2)
    installment_period = serializers.IntegerField()
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16)
    # status_id = serializers.CharField(max_length=2)
    phone_number = serializers.CharField(max_length=20)
    created_by_id = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        project_id, project_type_id, city_id = validated_data.pop('project_id'), validated_data.pop('project_type_id'), validated_data.pop('city_id')
        print(project_id, project_type_id, city_id)
        validated_data['pcp'] = PCP.objects.get_or_create(project=project_id, project_type=project_type_id, city=city_id)[0]
        validated_data['status'] = Status.objects.filter(code=1).first()# For Sale
        print(validated_data)
        return Land.objects.create(**validated_data)