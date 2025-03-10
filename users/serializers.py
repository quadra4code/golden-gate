from rest_framework import serializers
from users.models import CustomUser, UserPhoneNumber
from django.contrib.auth.hashers import make_password
import cloudinary.uploader

# Create your serializers here.

class RegisterSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=60, min_length=3)
    last_name = serializers.CharField(max_length=60, min_length=3, required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(max_length=20, min_length=8)
    email = serializers.EmailField(max_length=60, min_length=8, required=False, allow_blank=True, allow_null=True)
    image_url = serializers.CharField(max_length=1000, required=False, allow_blank=True, allow_null=True)
    user_type = serializers.CharField(max_length=2, default=5)
    interested_city = serializers.CharField(max_length=2, required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True)
    referral_code = serializers.CharField(max_length=12, required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'image_url', 'user_type', 'interested_city', 'password', 'referral_code']

    def create(self, validated_data):
        referral_code = validated_data.pop('referral_code', None)
        validated_data['interested_city_id'] = validated_data.pop('interested_city', None)
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

class AccountViewSerializer(serializers.ModelSerializer):
    account_type = serializers.CharField(source='get_user_type_display', read_only=True)
    interested_city_name = serializers.CharField(source='interested_city.name', read_only=True)
    interested_city = serializers.CharField(required=False, allow_null=True, write_only=True)
    phone_numbers = serializers.SerializerMethodField(read_only=True)
    referred_by_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'email_confirmed',
            'image_url',
            'referral_code',
            'referral_count',
            'phone_numbers',
            'is_active',
            'account_type',
            'interested_city_name',
            'interested_city',
            'referred_by_name'
        ]

    def get_referred_by_name(self, obj):
        return obj.referred_by.get_full_name() if obj.referred_by else None

    def get_phone_numbers(self, obj):
        return [
            {
                'pn_id': pn.id,
                'number': pn.phone_number,
                'pn_confirmed': pn.phone_number_confirmed,
                'is_main': pn.is_main_number
            }
            for pn in UserPhoneNumber.objects.filter(created_by_id=obj.id)
        ]

class UpdateAccountSerializer(serializers.ModelSerializer):
    phone_numbers_updated = serializers.BooleanField(write_only=True, default=False, allow_null=True)
    phone_numbers = serializers.ListField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'image', 'interested_city', 'user_type', 'phone_numbers_updated', 'phone_numbers']

    def update(self, instance, validated_data):
        # Handle image update
        new_image = validated_data.get('image', None)
        if new_image and instance.image:
            cloudinary.uploader.destroy(instance.image.public_id)
        instance.image = new_image if new_image else instance.image

        # Handle phone numbers
        if validated_data.get('phone_numbers_updated', False):
            new_phone_numbers = set(validated_data.get('phone_numbers', []))
            existing_phone_numbers = set(UserPhoneNumber.objects.filter(created_by=instance).values_list('phone_number', flat=True))

            # Find numbers to delete and new ones to add
            numbers_to_delete = existing_phone_numbers - new_phone_numbers
            numbers_to_add = new_phone_numbers - existing_phone_numbers

            # Delete old numbers
            UserPhoneNumber.objects.filter(created_by=instance, phone_number__in=numbers_to_delete).delete()

            # Insert new numbers
            UserPhoneNumber.objects.bulk_create([
                UserPhoneNumber(phone_number=num, created_by=instance)
                for num in numbers_to_add
            ])

        # Handle other fields
        for attr, value in validated_data.items():
            if attr not in ['phone_numbers', 'phone_numbers_updated']:
                setattr(instance, attr, value)
        instance.save()
        return instance





