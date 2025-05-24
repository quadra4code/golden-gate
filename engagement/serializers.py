from rest_framework import serializers
from engagement import models

# Create your serializers here.

class NotificationSerializer(serializers.ModelSerializer):
    city_obj = serializers.SerializerMethodField(read_only=True)
    unit_obj = serializers.SerializerMethodField(read_only=True)
    city_id = serializers.CharField(write_only=True)
    unit_id = serializers.CharField(write_only=True)
    is_read = serializers.BooleanField(source='is_deleted', read_only=True)
    class Meta:
        model = models.Notification
        fields = ['id', 'unit_id', 'city_id', 'city_obj', 'unit_obj', 'message', 'is_read']

    def get_city_obj(self, obj):
        if obj.city:
            return {
                'id': obj.city.id,
                'name': obj.city.name
            }
        return None
    
    def get_unit_obj(self, obj):
        if obj.unit:
            return {
                'id': obj.unit.id,
                'name': obj.unit.title
            }
        return None