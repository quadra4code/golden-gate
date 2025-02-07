from rest_framework import serializers
from users.models import CustomUser
from django.contrib.auth.hashers import make_password
# Create your serializers here.

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=60, min_length=3)
    last_name = serializers.CharField(max_length=60, min_length=3, required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(max_length=20, min_length=8)
    email = serializers.EmailField(max_length=60, min_length=8, required=False, allow_blank=True, allow_null=True)
    image_url = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    user_type = serializers.CharField(max_length=2, default=5)
    interested_city = serializers.CharField(max_length=40, required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'image_url', 'user_type', 'interested_city', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)