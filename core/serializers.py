from rest_framework import serializers

# Create your serializers here.

class LandSerializer(serializers.Serializer):
    project_id = serializers.CharField(max_length=3)
    project_type_id = serializers.CharField(max_length=2)
    city_id = serializers.CharField(max_length=2)
    first_installment_value = serializers.DecimalField(decimal_places=4, max_digits=16)
    installment_period = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)
    area = serializers.IntegerField()