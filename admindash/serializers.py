from rest_framework import serializers
from core import models as CoreModels
from core.constants import REQUEST_STATUS_CHOICES
from users import models as UsersModels
from django.contrib.auth.hashers import make_password

# Create your serializers here.

class GetAllUserSerializer(serializers.ModelSerializer):
    referred_by_name = serializers.CharField(source='referred_by.get_full_name', read_only=True)
    role = serializers.CharField(read_only=True)
    phone_numbers_list = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
    date_joined = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
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
    email = serializers.EmailField(max_length=60, min_length=8, required=False, allow_null=True)
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

class AllUnitSerializer(serializers.ModelSerializer):
    requests_count = serializers.IntegerField(read_only=True)
    over_price_obj = serializers.SerializerMethodField(read_only=True)
    total_price_obj = serializers.SerializerMethodField(read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True) # '%d-%b-%Y' => 01-jan-2025 | "%Y-%m-%d" => 2025-1-1
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    class Meta:
        model = CoreModels.Unit
        fields = ['id', 'title', 'over_price_obj', 'total_price_obj', 'created_at', 'requests_count', 'status_obj', 'hidden']

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.over_price:,.0f}', 'currency': obj.get_over_price_currency_display()} if obj.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.total_price:,.0f}', 'currency': obj.get_total_price_currency_display()} if obj.total_price else None

    def get_status_obj(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code, 'color': obj.status.color}

class UnitRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.CharField(source='created_by.id', read_only=True)
    first_name = serializers.CharField(source='created_by.first_name', read_only=True)
    last_name = serializers.CharField(source='created_by.last_name', read_only=True)
    username = serializers.CharField(source='created_by.username', read_only=True)
    email = serializers.CharField(source='created_by.email', read_only=True)
    email_confirmed = serializers.BooleanField(source='created_by.email_confirmed', read_only=True)
    is_active = serializers.BooleanField(source='created_by.is_active', read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d", source='created_by.last_login', read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d", source='created_by.date_joined', read_only=True)
    referral_code = serializers.CharField(source='created_by.referral_code', read_only=True)
    referral_count = serializers.CharField(source='created_by.referral_count', read_only=True)
    phone_numbers_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CoreModels.UnitRequest
        fields = [
            'id',
            'created_at',
            'status_obj',
            'status_msg',
            'user_id',
            'first_name',
            'last_name',
            'username',
            'email',
            'email_confirmed',
            'is_active',
            'last_login',
            'date_joined',
            'referral_code',
            'referral_count',
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
                for pn in UsersModels.UserPhoneNumber.objects.filter(created_by=obj.created_by).order_by('created_at')
            ]

    def get_status_obj(self, obj):
        status_obj = REQUEST_STATUS_CHOICES.get(obj.status)
        return {'name': status_obj.get('name'), 'color': status_obj.get('color')}

class AllRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(source='unit.title', read_only=True)
    over_price_obj = serializers.SerializerMethodField(read_only=True)
    total_price_obj = serializers.SerializerMethodField(read_only=True)
    unit_status_obj = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.CharField(source='created_by.id', read_only=True)
    first_name = serializers.CharField(source='created_by.first_name', read_only=True)
    last_name = serializers.CharField(source='created_by.last_name', read_only=True)
    username = serializers.CharField(source='created_by.username', read_only=True)
    email = serializers.CharField(source='created_by.email', read_only=True)
    email_confirmed = serializers.BooleanField(source='created_by.email_confirmed', read_only=True)
    is_active = serializers.BooleanField(source='created_by.is_active', read_only=True)
    last_login = serializers.DateTimeField(format="%Y-%m-%d", source='created_by.last_login', read_only=True)
    phone_numbers_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CoreModels.UnitRequest
        fields = [
            'id',
            'created_at',
            'status_obj',
            'title',
            'over_price_obj',
            'total_price_obj',
            'unit_status_obj',
            'status_msg',
            'user_id',
            'first_name',
            'last_name',
            'username',
            'email',
            'email_confirmed',
            'is_active',
            'last_login',
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
                for pn in UsersModels.UserPhoneNumber.objects.filter(created_by=obj.created_by).order_by('created_at')
            ]

    def get_status_obj(self, obj):
        status_obj = REQUEST_STATUS_CHOICES.get(obj.status)
        return {'name': status_obj.get('name'), 'color': status_obj.get('color')}

    def get_unit_status_obj(self, obj):
        return {'name': obj.unit.status.name, 'code': obj.unit.status.code, 'color': obj.unit.status.color}

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.unit.over_price:,.0f}', 'currency': obj.unit.get_over_price_currency_display()} if obj.unit.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.unit.total_price:,.0f}', 'currency': obj.unit.get_total_price_currency_display()} if obj.unit.total_price else None

