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
    unit_type = serializers.CharField(source='unit_type.name', read_only=True)
    project = serializers.CharField(source='project.name', read_only=True)
    city = serializers.CharField(source='city.name', read_only=True)
    unit_number = serializers.CharField(read_only=True)
    building_number = serializers.CharField(read_only=True)
    floor = serializers.CharField(source="get_floor_display", read_only=True)
    over_price_obj = serializers.SerializerMethodField(read_only=True)
    total_price_obj = serializers.SerializerMethodField(read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True) # '%d-%b-%Y' => 01-jan-2025 | "%Y-%m-%d" => 2025-1-1
    updated_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True) # '%d-%b-%Y' => 01-jan-2025 | "%Y-%m-%d" => 2025-1-1
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    class Meta:
        model = CoreModels.Unit
        fields = [
            'id',
            'title',
            'over_price_obj',
            'total_price_obj',
            'created_at',
            'updated_at',
            'requests_count',
            'unit_type',
            'project',
            'proposal_str',
            'city',
            'unit_number',
            'building_number',
            'floor',
            'status_obj',
            'hidden',
            'featured',
            'is_approved',
            'approver_message'
        ]

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.over_price:,.0f}', 'currency': obj.get_over_price_currency_display()} if obj.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.total_price:,.0f}', 'currency': obj.get_total_price_currency_display()} if obj.total_price else None

    def get_status_obj(self, obj):
        return {'id': obj.status.id, 'name': obj.status.name, 'code': obj.status.code, 'color': obj.status.color}

class UnitRequestSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.CharField(source='created_by.id', read_only=True)
    first_name = serializers.CharField(source='created_by.first_name', read_only=True)
    last_name = serializers.CharField(source='created_by.last_name', read_only=True)
    username = serializers.CharField(source='created_by.username', read_only=True)
    email = serializers.CharField(source='created_by.email', read_only=True)
    email_confirmed = serializers.BooleanField(source='created_by.email_confirmed', read_only=True)
    is_active = serializers.BooleanField(source='created_by.is_active', read_only=True)
    last_login = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", source='created_by.last_login', read_only=True)
    date_joined = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", source='created_by.date_joined', read_only=True)
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
    created_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
    updated_at = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", read_only=True)
    status_obj = serializers.SerializerMethodField(read_only=True)
    sales_obj = serializers.SerializerMethodField(read_only=True)
    title = serializers.CharField(source='unit.title', read_only=True)
    unit_type = serializers.CharField(source='unit.unit_type.name', read_only=True)
    project = serializers.CharField(source='unit.project.name', read_only=True)
    city = serializers.CharField(source='unit.city.name', read_only=True)
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
    last_login = serializers.DateTimeField(format="%d-%m-%Y | %I:%M:%S %p", source='created_by.last_login', read_only=True)
    phone_numbers_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CoreModels.UnitRequest
        fields = [
            'id',
            'created_at',
            'updated_at',
            'status_obj',
            'sales_obj',
            'title',
            'unit_type',
            'project',
            'city',
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
        return {'code': obj.status, 'name': status_obj.get('name'), 'color': status_obj.get('color')}

    def get_unit_status_obj(self, obj):
        return {'name': obj.unit.status.name, 'code': obj.unit.status.code, 'color': obj.unit.status.color}

    def get_over_price_obj(self, obj):
        return {'price_type': 'الأوفر', 'price_value': f'{obj.unit.over_price:,.0f}', 'currency': obj.unit.get_over_price_currency_display()} if obj.unit.over_price else None
    
    def get_total_price_obj(self, obj):
        return {'price_type': 'الإجمالى', 'price_value': f'{obj.unit.total_price:,.0f}', 'currency': obj.unit.get_total_price_currency_display()} if obj.unit.total_price else None

    def get_sales_obj(self, obj):
        return {'id': obj.sales_staff.id, 'name': obj.sales_staff.get_full_name()} if obj.sales_staff else None
        # sales_staff = obj.salesrequest_set.first()
        # return {'id': sales_staff.id, 'name': sales_staff.get_full_name()} if sales_staff else None


class ClientReviewSerializer(serializers.ModelSerializer):
    client_obj = serializers.SerializerMethodField(read_only=True)
    is_hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    class Meta:
        model = CoreModels.ClientReview
        fields = ['id', 'rate', 'review', 'created_at', 'client_obj', 'is_hidden']

    def get_client_obj(self, obj):
        return {
            'id': obj.created_by.id,
            'first_name': obj.created_by.first_name,
            'last_name': obj.created_by.last_name,
            'phone_number': obj.created_by.username,
            'email': obj.created_by.email,
            'email_confirmed': obj.created_by.email_confirmed,
            'image': obj.created_by.image.url if obj.created_by.image else None,
        }

class UnitTypeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)

    class Meta:
        model = CoreModels.UnitType
        fields = ['id', 'name', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None

class ProposalSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)

    class Meta:
        model = CoreModels.Proposal
        fields = ['id', 'name', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None


class ProjectSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)
    relation = serializers.SerializerMethodField()
    unit_type_ids = serializers.ListField(write_only=True)
    class Meta:
        model = CoreModels.Project
        fields = ['id', 'name', 'relation', 'unit_type_ids', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None

    def get_relation(self, obj):
        unit_types = obj.unittypeproject_set.all()
        return [{'unit_type_id': ut.unit_type.id, 'unit_type_name': ut.unit_type.name} for ut in unit_types]

    def create(self, validated_data):
        unit_type_ids = validated_data.pop('unit_type_ids', [])
        project = super().create(validated_data)
        unit_types_projects = [
            CoreModels.UnitTypeProject(project=project, unit_type_id=id)
            for id in unit_type_ids]
        CoreModels.UnitTypeProject.objects.bulk_create(unit_types_projects)
        return project

    def update(self, instance, validated_data):
        unit_type_ids = validated_data.pop('unit_type_ids', [])
        instance = super().update(instance, validated_data)
        # Clear existing relations
        instance.unittypeproject_set.all().delete()
        # Create new relations
        unit_types_projects = [
            CoreModels.UnitTypeProject(project=instance, unit_type_id=id)
            for id in unit_type_ids]
        CoreModels.UnitTypeProject.objects.bulk_create(unit_types_projects)
        return instance

class CitySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)

    class Meta:
        model = CoreModels.City
        fields = ['id', 'name', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None


class RegionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    city_id = serializers.CharField(write_only=True)
    city_obj = serializers.SerializerMethodField()
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)

    class Meta:
        model = CoreModels.Region
        fields = ['id', 'name', 'city_id', 'city_obj', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None

    def get_city_obj(self, obj):
        if obj.city:
            return {"city_id": obj.city.id, "city_name": obj.city.name}
        return None

class StatusSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    updated_at = serializers.DateTimeField(format='%d-%m-%Y | %I:%M:%S %p', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    created_by_id = serializers.CharField(write_only=True)
    updated_by_id = serializers.CharField(write_only=True)
    hidden = serializers.BooleanField(source='is_deleted', read_only=True)

    class Meta:
        model = CoreModels.Status
        fields = ['id', 'name', 'code', 'color', 'created_at', 'updated_at', 'created_by_id', 'updated_by_id', 'created_by_name', 'updated_by_name', 'hidden']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return None

    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}".strip()
        return None




