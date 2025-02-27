from rest_framework import serializers
from core import models as CoreModels
from users import models as UsersModels
from django.contrib.auth.hashers import make_password

# Create your serializers here.

class GetAllUserSerializer(serializers.ModelSerializer):
    referred_by_name = serializers.CharField(source='referred_by.get_full_name', read_only=True)
    role = serializers.CharField(read_only=True)
    phone_numbers_list = serializers.SerializerMethodField()
    class Meta:
        model = UsersModels.CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'email_confirmed',
            'is_active',
            'last_login',
            'date_joined',
            'role',
            'referral_code',
            'referral_count',
            'referred_by_name',
            'phone_numbers_list'
        ]
    
    def get_phone_numbers_list(self, obj):
        return [
                {
                    'phone_number_id': pn.id,
                    'phone_number': pn.phone_number,
                    'is_main': pn.is_main_number,
                    'phone_number_confirmed': pn.phone_number_confirmed
                }
                for pn in UsersModels.UserPhoneNumber.objects.filter(created_by=obj).order_by('created_at')
            ]

class AddStaffSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=60, min_length=3)
    last_name = serializers.CharField(max_length=60, min_length=3, required=False, allow_blank=True, allow_null=True)
    username = serializers.CharField(max_length=20, min_length=8)
    email = serializers.EmailField(max_length=60, min_length=8, required=False, allow_blank=True, allow_null=True)
    role_name = serializers.CharField(max_length=20, write_only=True)
    class Meta:
        model = UsersModels.CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'role_name']

    def create(self, validated_data):
        role_name = validated_data.pop("role_name")
        user_type_dict = dict(UsersModels.CustomUser.USER_TYPE_CHOICES)
        reverse_user_type_dict = {v: k for k, v in user_type_dict.items()}
        user_type = reverse_user_type_dict.get(role_name)
        if user_type is None:
            raise serializers.ValidationError({"role_name": "مستوى الصلاحية غير صالح"})
        validated_data['user_type'] = user_type
        validated_data['is_staff'] = True
        validated_data['password'] = make_password("123")
        new_user = super().create(validated_data)
        return new_user

class AllUnitRequestSerializer(serializers.ModelSerializer):
    request_count = serializers.SerializerMethodField(read_only=True)
    unit_status = serializers.CharField(source='unit.status.name', read_only=True)
    class Meta:
        model = CoreModels.UnitRequest
        fields = ['id', 'unit', 'created_at', 'requests_count', 'unit_status']
    
    def get_request_count(self, obj):
        return CoreModels.UnitRequest.objects.filter(unit=obj.unit).count()


