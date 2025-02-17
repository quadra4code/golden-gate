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
    referral_code = serializers.CharField(max_length=12, required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'image_url', 'user_type', 'interested_city', 'password', 'referral_code']

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        validated_data['password'] = make_password(validated_data['password'])
        referrer = None
        if referral_code:  # If the user used a referral code
            try:
                referrer = CustomUser.objects.get(referral_code=referral_code)
                validated_data['referred_by'] = referrer
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({"referral_code": "كود الدعوة غير صالح"})
        new_user = super().create(validated_data)
        # If the user was referred, increment referrer's count
        if referrer:
            referrer.referral_count += 1
            referrer.save(update_fields=['referral_count'])
        return new_user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)