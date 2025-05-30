from core import models as CoreModels
from core.constants import REQUEST_STATUS_CHOICES
from core import serializers as CoreSerializers
from engagement import models as EngagementModels
from users import models as UsersModels
from django.contrib.auth.models import Group
from admindash import serializers as AdminSerializers, models as AdminModels
from core.base_models import ResultView
from django.db.models import Value, CharField, Q, Count
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from users.utils import generate_jwt_token
from admindash import utils
import logging

# Create your services here.

# region Statistics
def main_statistics_service():
    result = ResultView()
    try:
        # Fetch status objects once
        status_0 = CoreModels.Status.objects.get(code=0)
        status_3 = CoreModels.Status.objects.get(code=3)
        # Fetch all units and annotate counts
        units_stats = CoreModels.Unit.objects.aggregate(
            all_units=Count('id'),
            requested_units=Count('id', filter=Q(status=status_0)),
            sold_units=Count('id', filter=Q(status=status_3)),
        )
        # Fetch all requests and annotate counts
        requests_stats = CoreModels.UnitRequest.objects.aggregate(
            all_requests=Count('id'),
            responded_requests=Count('id', filter=~Q(status=0)),
        )
        # Fetch all clients and annotate counts
        clients_stats = UsersModels.CustomUser.objects.aggregate(
            all_clients=Count('id', filter=Q(user_type__in=[5, 6, 7])),
            managers=Count('id', filter=Q(user_type=1)),
            admins=Count('id', filter=Q(user_type=3)),
            sales=Count('id', filter=Q(user_type=4)),
            buyers=Count('id', filter=Q(user_type=5)),
            sellers=Count('id', filter=Q(user_type=6)),
            brokers=Count('id', filter=Q(user_type=7)),
        )
        
        # Combine results
        result.data = {
            'all_units': units_stats['all_units'],
            'requested_units': units_stats['requested_units'],
            'sold_units': units_stats['sold_units'],
            'all_requests': requests_stats['all_requests'],
            'responded_requests': requests_stats['responded_requests'],
            'all_clients': clients_stats['all_clients'],
            # 'active_visitors_count': utils.get_active_visitors_count(),
            'managers': clients_stats['managers'],
            'admins': clients_stats['admins'],
            'sales': clients_stats['sales'],
            'buyers': clients_stats['buyers'],
            'sellers': clients_stats['sellers'],
            'brokers': clients_stats['brokers'],
        }
        result.msg = 'تم جلب الإحصائيات بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الإحصائيات'
        result.data = {'errors': str(e)}
    finally:
        return result

def active_visitors_count_service():
    result = ResultView()
    try:
        active_visitors_count = utils.get_active_visitors_count()
        result.data = {
            'active_visitors_count': active_visitors_count
        }
        result.msg = 'تم جلب عدد الزوار الحالى بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ إثناء جلب عدد الزوار الحالى'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion
# region Staff
def staff_login_service(request_data):
    result = ResultView()
    logger = logging.getLogger(__name__)
    try:
        username = request_data.get('username', '').strip()
        password = request_data.get('password', '').strip()
        if not username or not password:
            result.msg = 'رقم الهاتف مطلوب' if password else 'كلمة السر مطلوبة' if username  else 'رقم الهاتف وكلمة السر مطلوبين'
        else:
            user_to_auth = authenticate(username=username, password=password)
            if user_to_auth is None:
                logger.warning(f"Failed login attempt for username {username}.")
                result.msg = 'خطأ فى بيانات الحساب'
            elif user_to_auth.is_staff == False:
                result.msg = 'هذا المستخدم غير مصرح له بالدخول'
            elif not user_to_auth.is_active:
                result.msg = 'الحساب غير مفعل؛ برجاء التواصل مع الدعم'
            else:
                logger.info(f"User {user_to_auth.username} logged in successfully.")
                token_obj = generate_jwt_token(user_to_auth)
                result.msg = 'تم تسجيل الدخول بنجاح'
                result.data = {
                    'refresh_token': token_obj.get('refresh'),
                    'access_token': token_obj.get('access'),
                    'user': {
                        'id': user_to_auth.id,
                        'username': user_to_auth.username,
                        'full_name': user_to_auth.get_full_name(),
                        'referral_code': user_to_auth.referral_code,
                        'role': ' | '.join(([gr.name for gr in user_to_auth.groups.all()])).strip() if user_to_auth.groups.exists() else 'No Role'
                    }
                }
                result.is_success = True
    except Exception as e:
        result.msg = f'حدث خطأ أثناء تسجيل الدخول للمستخدم {username}.'
        result.data = {'error': str(e)}
    finally:
        return result

def paginated_staff_service(request_data):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 10)
        all_staff_q = (
            UsersModels.CustomUser.objects
            .filter(~Q(groups__name='Superuser') & ~Q(groups__name='Client'))
            .annotate(
                role=Coalesce(
                    StringAgg('groups__name', ', ', output_field=CharField()),
                    Value('No Group', output_field=CharField())
                )
            )
            .exclude(role='No Group')
        )
        roles = Group.objects.all().exclude(name__in=["Client", "Superuser"]).values('id', 'name')
        all_staff_count = all_staff_q.count()
        if all_staff_count <= 0:
            raise ValueError('لا يوجد موظفين للعرض')
        total_pages = (all_staff_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        all_staff_q = all_staff_q[start_index:end_index]
        serialized_staff = AdminSerializers.GetAllUserSerializer(all_staff_q, many=True)
        result.data = {
            "all": serialized_staff.data,
            "permissions": roles,
            "pagination": {
                "total_items": all_staff_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الموظفين بنجاح'
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الموظفين'
        result.data = {'errors': str(e)}
    finally:
        return result

def staff_roles_service():
    result = ResultView()
    try:
        roles = Group.objects.all().exclude(name__in=["Client", "Superuser"]).values('id', 'name')
        result.data = list(roles)
        result.is_success = True
        result.msg = 'تم جلب مستويات الصلاحيات بنجاح'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب مستويات الصلاحيات'
        result.data = {'errors': str(e)}
    finally:
        return result

def add_staff_service(request_data):
    result = ResultView()
    try:
        new_staff = AdminSerializers.AddStaffSerializer(data=request_data)
        if new_staff.is_valid():
            new_staff.save()
            UsersModels.UserPhoneNumber.objects.create(
                    phone_number=new_staff.instance.username,
                    is_main_number=True,
                    created_by=new_staff.instance
                )
            client_group, created = Group.objects.get_or_create(name=request_data.get('role_name'))
            new_staff.instance.groups.add(client_group)
            all_staff_result = paginated_staff_service({})
            if all_staff_result.is_success:
                result.data = all_staff_result.data
                result.is_success = True
                result.msg = 'تم إضافة الموظف بنجاح'
            else:
                raise ValueError('تم إضافة الموظف بنجاح ولكن حدث خطأ أثناء جلب بيانات جميع الموظفين')
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات الموظف'
            result.data = new_staff.errors
    except ValueError as ve:
        result.msg = str(ve)
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إضافة الموظف'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_active_user_service(user_id):
    result = ResultView()
    try:
        user_obj = UsersModels.CustomUser.objects.get(id=user_id)
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        result.is_success = True
        result.msg = f'{'تم تفعيل' if user_obj.is_active else 'تم إلغاء تفعيل'} الحساب بنجاح'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تغيير حالة الحساب'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_staff_service(staff_id):
    result = ResultView()
    try:
        user_obj = UsersModels.CustomUser.objects.get(id=staff_id)
        user_obj.groups.clear()
        phone_numbers = UsersModels.UserPhoneNumber.objects.filter(created_by=user_obj)
        phone_numbers.delete() if phone_numbers.exists() else None
        user_obj.delete()
        result.is_success = True
        result.msg = 'تم حذف الموظف بنجاح'
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف الموظف'
        result.data = {'errors': str(e)}
    finally:
        return result

def change_staff_permissions_service(request_data):
    result = ResultView()
    try:
        staff_obj = UsersModels.CustomUser.objects.prefetch_related("groups").get(id=request_data.get('staff_id', 0), is_staff=True)
        current_group_names = set(staff_obj.groups.values_list("name", flat=True))
        new_group_names = set(request_data.get("perms_list", []))
        if current_group_names != new_group_names:
            staff_obj.groups.clear()
            staff_obj.groups.add(*Group.objects.filter(name__in=new_group_names))
        result.msg = f'تم تغيير صلاحيات {staff_obj.get_full_name()} بنجاح'
        result.is_success = True
    except UsersModels.CustomUser.DoesNotExist as e:
        result.msg = 'الموظف غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تغيير صلاحيات الموظف'
        result.data = {'errors': str(e)}
    finally:
        return result

def get_sales_staff_service():
    result = ResultView()
    try:
        sales_staff = UsersModels.CustomUser.objects.filter(~Q(groups__name='Superuser') & ~Q(groups__name='Client'))
        serialized_sales_staff = AdminSerializers.GetAllUserSerializer(sales_staff, many=True)
        result.data = serialized_sales_staff.data
        result.msg = 'تم جلب موظفين المبيعات بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب موظفين المبيعات'
        result.data = {'errors': str(e)}
    finally:
        return result

def reset_password_service(user_id):
    result = ResultView()
    try:
        user_obj = UsersModels.CustomUser.objects.get(id=user_id)
        user_obj.set_password('123')
        user_obj.save()
        result.msg = 'تم إعادة تعيين كلمة السر بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إعادة تعيين كلمة السر'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Client
def paginated_clients_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        all_clients_q = UsersModels.CustomUser.objects.filter(groups__name='Client')
        all_clients_count = all_clients_q.count()
        if all_clients_count <= 0:
            raise ValueError('لا يوجد عملاء للعرض')
        total_pages = (all_clients_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        all_clients_q = all_clients_q[start_index:end_index]
        serialized_clients = AdminSerializers.GetAllUserSerializer(all_clients_q, many=True)
        result.data = {
            "all": serialized_clients.data,
            "pagination": {
                "total_items": all_clients_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات العملاء بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = []
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات العملاء'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Unit
def unit_requests_user_service(unit_id):
    result = ResultView()
    try:
        all_unit_requests_query = CoreModels.UnitRequest.objects.filter(unit__id=unit_id).order_by('created_at')
        all_unit_requests_count = all_unit_requests_query.count()
        if all_unit_requests_count <= 0:
            raise ValueError('لا يوجد طلبات لهذه الوحدة')
        serialized_user_requests = AdminSerializers.UnitRequestSerializer(all_unit_requests_query, many=True)
        result.data = serialized_user_requests.data
        result.is_success = True
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب طلبات هذه الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def paginated_units_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))

        filter_kwargs = {
            'is_deleted': False,
            'is_approved': True
        }

        optional_filters = {
            'status_id': request_data.get('status_id', None),
            'unit_type_id': request_data.get('unit_type_id', None),
            'project_id': request_data.get('project_id', None),
            'city_id': request_data.get('city_id', None)
        }

        filter_kwargs.update({
            k: v for k, v in optional_filters.items() if v is not None
        })
        all_units_q = CoreModels.Unit.objects.annotate(
            requests_count=Count('unitrequest')  # Assuming 'unitrequest' is the related name
        ).filter(**filter_kwargs).order_by('-requests_count')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات متاحة للعرض')
        total_pages = (all_units_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        all_units_q = all_units_q[start_index:end_index]
        serialized_units = AdminSerializers.AllUnitSerializer(all_units_q, many=True)
        statuses = CoreSerializers.StatusSerializer(CoreModels.Status.objects.all(), many=True)
        result.data = {
            "all": serialized_units.data,
            "statuses": statuses.data,
            "pagination": {
                "total_items": all_units_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الوحدات بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الوحدات'
        result.data = {'errors': str(e)}
    finally:
        return result

def paginated_featured_units_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        
        filter_kwargs = {
            'is_deleted': False,
            'featured': True
        }

        optional_filters = {
            'status_id': request_data.get('status_id', None),
            'unit_type_id': request_data.get('unit_type_id', None),
            'project_id': request_data.get('project_id', None),
            'city_id': request_data.get('city_id', None)
        }

        filter_kwargs.update({
            k: v for k, v in optional_filters.items() if v is not None
        })
        all_units_q = CoreModels.Unit.objects.annotate(
            requests_count=Count('unitrequest')  # Assuming 'unitrequest' is the related name
        ).filter(**filter_kwargs).order_by('created_at')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات مميزة متاحة للعرض')
        paginator = Paginator(all_units_q, page_size)
        page = paginator.get_page(page_number)
        serialized_units = AdminSerializers.AllUnitSerializer(page.object_list, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الوحدات المميزة بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الوحدات المميزة'
        result.data = {'errors': str(e)}
    finally:
        return result

def paginated_units_addition_requests_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        
        filter_kwargs = {
            'is_deleted': False,
            'is_approved': None
        }

        optional_filters = {
            'status_id': request_data.get('status_id', None),
            'unit_type_id': request_data.get('unit_type_id', None),
            'project_id': request_data.get('project_id', None),
            'city_id': request_data.get('city_id', None)
        }

        filter_kwargs.update({
            k: v for k, v in optional_filters.items() if v is not None
        })
        all_units_q = CoreModels.Unit.objects.filter(**filter_kwargs).order_by('created_at')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات جديدة متاحة للعرض')
        paginator = Paginator(all_units_q, page_size)
        page = paginator.get_page(page_number)
        serialized_units = AdminSerializers.AllUnitSerializer(page.object_list, many=True)
        # statuses = CoreSerializers.StatusSerializer(CoreModels.Status.objects.all(), many=True)
        result.data = {
            "all": serialized_units.data,
            # "statuses": statuses.data,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الوحدات الجديدة بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الوحدات الجديدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def paginated_soft_deleted_units_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        
        filter_kwargs = {
            'is_deleted': True
        }

        optional_filters = {
            'status_id': request_data.get('status_id', None),
            'unit_type_id': request_data.get('unit_type_id', None),
            'project_id': request_data.get('project_id', None),
            'city_id': request_data.get('city_id', None)
        }

        filter_kwargs.update({
            k: v for k, v in optional_filters.items() if v is not None
        })
        all_units_q = CoreModels.Unit.objects.annotate(
            requests_count=Count('unitrequest')  # Assuming 'unitrequest' is the related name
        ).filter(**filter_kwargs).order_by('-updated_at')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد وحدات محذوفة متاحة للعرض')
        paginator = Paginator(all_units_q, page_size)
        page = paginator.get_page(page_number)
        serialized_units = AdminSerializers.AllUnitSerializer(page.object_list, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الوحدات المحذوفة بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الوحدات المحذوفة'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_unit_status_service(unit_id, status_id, user_id):
    result = ResultView()
    try:
        unit_obj = CoreModels.Unit.objects.get(id=unit_id)
        unit_obj.status_id = status_id
        unit_obj.updated_by_id = user_id
        unit_obj.save()
        result.data = {
            'id': unit_obj.status.id,
            'name': unit_obj.status.name,
            'code': unit_obj.status.code,
            'color': unit_obj.status.color
        }
        result.is_success = True
        result.msg = 'تم تحديث حالة الوحدة بنجاح'
    except CoreModels.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث حالة الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_unit_deleted_service(unit_id, user_id):
    result = ResultView()
    try:
        unit_obj = CoreModels.Unit.objects.get(id=unit_id)
        unit_obj.is_deleted = not unit_obj.is_deleted
        unit_obj.updated_by_id = user_id
        unit_obj.save()
        result.is_success = True
        result.msg = f'تم {'إخفاء' if unit_obj.is_deleted else 'إظهار'} الوحدة بنجاح'
    except CoreModels.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إخفاء الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_unit_featured_service(unit_id, user_id):
    result = ResultView()
    try:
        unit_obj = CoreModels.Unit.objects.get(id=unit_id)
        unit_obj.featured = not unit_obj.featured
        unit_obj.updated_by_id = user_id
        unit_obj.save()
        result.is_success = True
        result.msg = f'تم جعل الوحدة {'مميزة' if unit_obj.featured else 'غير مميزة'} بنجاح'
    except CoreModels.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تعديل تميز الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def approve_unit_addition_service(unit_id, user_id):
    result = ResultView()
    try:
        unit_obj = CoreModels.Unit.objects.get(id=unit_id)
        unit_obj.is_approved = True
        unit_obj.updated_by_id = user_id
        unit_obj.save()
        EngagementModels.Notification.objects.create(unit_id=unit_id, message='تم قبول طلب إضافة وحدتكم بنجاح', created_by=unit_obj.created_by)
        result.is_success = True
        result.msg = 'تم قبول طلب إضافة الوحدة وإرسال إشعار للمستخدم بنجاح'
    except CoreModels.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء قبول طلب إضافة الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result

def disapprove_unit_addition_service(request_data, user_id):
    result = ResultView()
    try:
        unit_id = request_data.get('unit_id', None)
        approver_message = request_data.get('message', None)
        unit_obj = CoreModels.Unit.objects.get(id=unit_id)
        unit_obj.updated_by_id = user_id
        unit_obj.approver_message = approver_message if approver_message else ''
        unit_obj.is_approved = False
        unit_obj.save()
        msg = f'تم رفض طلب إضافة وحدتكم للأسباب الآتية: {approver_message}'
        EngagementModels.Notification.objects.create(unit_id=unit_id, message=msg, created_by=unit_obj.created_by)
        result.is_success = True
        result.msg = f'تم رفض طلب إضافة الوحدة وإرسال إشعار للمستخدم بنجاح'
    except CoreModels.Unit.DoesNotExist as e:
        result.msg = 'الوحدة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء رفض طلب إضافة الوحدة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Request
def paginated_requests_service(request_data, staff_obj):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 12)
        filter_kwargs = {
            'is_deleted': False
        }

        optional_filters = {
            'status': request_data.get('status_id', None),
            'unit__unit_type_id': request_data.get('unit_type_id', None),
            'unit__project_id': request_data.get('project_id', None),
            'unit__city_id': request_data.get('city_id', None)
        }

        filter_kwargs.update({
            k: v for k, v in optional_filters.items() if v is not None
        })
        all_requests = CoreModels.UnitRequest.objects.filter(**filter_kwargs)
        if staff_obj.groups.filter(name='Sales').exists() and not staff_obj.groups.filter(name__in=['Superuser', "Manager", "Admin"]):
            sales_requests = AdminModels.SalesRequest.objects.filter(sales=staff_obj).values_list('request_id', flat=True)
            all_requests = all_requests.filter(id__in=sales_requests)
        else:
            sales_staff = UsersModels.CustomUser.objects.filter(groups__name="Sales")
            serialized_sales_staff = AdminSerializers.GetAllUserSerializer(sales_staff, many=True)
            result.data = {
                "sales_staff": serialized_sales_staff.data
            }
        paginator = Paginator(all_requests.order_by('-updated_at'), page_size)
        page = paginator.get_page(page_number)
        serialized_requests = AdminSerializers.AllRequestSerializer(page.object_list, many=True)
        result.data = {
            "all": serialized_requests.data,
            "request_statuses": [{'code': key, 'label': val.get("name"), 'color': val.get("color")} for key, val in REQUEST_STATUS_CHOICES.items()],
            "sales_staff": result.data['sales_staff'] if result.data else None,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
        result.is_success = True
        result.msg = 'تم جلب الطلبات بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث حالة الطلب'
        result.data = {'errors': str(e)}
    finally:
        return result

def change_request_status_service(request_data, admin_obj):
    result = ResultView()
    try:
        request_id = request_data.get('request_id', None)
        status_id = request_data.get('status_id', None)
        status_msg = request_data.get('status_msg', None)
        request_obj = CoreModels.UnitRequest.objects.get(id=request_id)
        if status_id or status_msg:
            request_obj.status = status_id if status_id else request_obj.status
            request_obj.status_msg = status_msg if status_msg else request_obj.status_msg
            request_obj.updated_by = admin_obj
            request_obj.save()
        result.is_success = True
        result.msg = 'تم تحديث حالة الطلب بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.data = {'errors': str(ve)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث حالة الطلب'
        result.data = {'errors': str(e)}
    finally:
        return result

def assign_sales_request_service(request_data, admin_obj):
    result = ResultView()
    try:
        _, created = AdminModels.SalesRequest.objects.update_or_create(
            sales_id=request_data.get('sales_id'),
            request_id=request_data.get('request_id'),
            created_by=admin_obj
        )
        result.msg = f'تم تعيين {_.sales.get_full_name()} على الطلب بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تعيين موظف المبيعات على الطلب'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Contact Us
def paginated_contact_msgs_service(request_data):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 10)
        all_msgs_q = CoreModels.ContactUs.objects.all()
        all_msgs_count = all_msgs_q.count()
        if all_msgs_count <= 0:
            raise ValueError('لا يوجد رسائل للعرض')
        total_pages = (all_msgs_count + page_size - 1) // page_size
        page_number = min(page_number, total_pages)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        all_msgs_q = all_msgs_q[start_index:end_index]
        serialized_msgs = CoreSerializers.ContactUsSerializer(all_msgs_q, many=True)
        result.data = {
            "all": serialized_msgs.data,
            "pagination": {
                "total_items": all_msgs_count,
                "total_pages": total_pages,
                "current_page": page_number,
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الرسائل بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
        result.data = {
            "all": []
        }
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الرسائل'
        result.data = {'errors': str(e)}
    finally:
        return result

def solve_contact_msg_service(msg_id, user_id):
    result = ResultView()
    try:
        msg_obj = CoreModels.ContactUs.objects.get(id=msg_id)
        msg_obj.is_deleted = True
        msg_obj.updated_by_id = user_id
        msg_obj.save()
        result.msg = 'تم حل المشكلة بنجاح'
        result.is_success = True
    except CoreModels.ContactUs.DoesNotExist as e:
        result.msg = 'الرسالة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حل المشكلة'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_contact_msg_service(msg_id):
    result = ResultView()
    try:
        msg_obj = CoreModels.ContactUs.objects.filter(id=msg_id).delete()
        result.msg = 'تم حذف المشكلة بنجاح'
        result.is_success = True
    except CoreModels.ContactUs.DoesNotExist as e:
        result.msg = 'الرسالة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف المشكلة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Article
def create_article_service(request_data, admin_id):
    result = ResultView()
    try:
        request_data['created_by_id'] = admin_id
        serialized_new_article = CoreSerializers.ArticleSerializer(data=request_data)
        if serialized_new_article.is_valid():
            serialized_new_article.save()
            result.msg = 'تم إضافة المقالة بنجاح'
            result.data = CoreSerializers.ArticleSerializer(CoreModels.Article.objects.order_by('-updated_at'), many=True).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات المقالة'
            result.data = serialized_new_article.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ المقالة'
        result.data = {'errors': str(e)}
    finally:
        return result

def read_articles_service():
    result = ResultView()
    try:
        all_articles = CoreModels.Article.objects.order_by('-updated_at')
        serialized_all_articles = CoreSerializers.ArticleSerializer(all_articles, many=True)
        result.data = serialized_all_articles.data
        result.msg = 'تم جلب المقالات بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب المقالات'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_article_service(request_data, admin_id, article_id):
    result = ResultView()
    try:
        request_data['updated_by_id'] = admin_id
        old_article = CoreModels.Article.objects.get(id=article_id)
        serialized_update_article = CoreSerializers.ArticleSerializer(old_article, data=request_data, partial=True)
        if serialized_update_article.is_valid():
            serialized_update_article.save()
            result.msg = 'تم تحديث المقالة بنجاح'
            result.data = CoreSerializers.ArticleSerializer(CoreModels.Article.objects.order_by('-updated_at'), many=True).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات المقالة'
            result.data = serialized_update_article.errors
    except CoreModels.Article.DoesNotExist as e:
        result.msg = 'المقالة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث المقالة'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_article_service(article_id):
    result = ResultView()
    try:
        delete_count, _ = CoreModels.Article.objects.filter(id=article_id).delete()
        if delete_count == 0:
            raise CoreModels.Article.DoesNotExist()
        result.msg = 'تم حذف المقالة بنجاح'
        result.is_success = True
    except CoreModels.Article.DoesNotExist as e:
        result.msg = 'المقالة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف المقالة'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_hidden_article_service(article_id, admin_obj):
    result = ResultView()
    try:
        article = CoreModels.Article.objects.get(id=article_id)
        article.is_deleted = not article.is_deleted
        article.updated_by = admin_obj
        article.save()
        result.msg = f'تم {'إخفاء' if article.is_deleted else 'إظهار'} المقالة بنجاح'
        result.data = CoreSerializers.ArticleSerializer(article).data
        result.is_success = True
    except CoreModels.Article.DoesNotExist as e:
        result.msg = 'المقالة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إخفاء / إظهار المقالة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Consultation Type
def create_consult_type_service(request_data, admin_id):
    result = ResultView()
    try:
        request_data['created_by_id'] = admin_id
        serialized_new_consult_type = CoreSerializers.ConsultationTypeSerializer(data=request_data)
        if serialized_new_consult_type.is_valid():
            serialized_new_consult_type.save()
            result.msg = 'تم إضافة نوع الإستشارة بنجاح'
            result.data = CoreSerializers.ConsultationTypeSerializer(CoreModels.ConsultationType.objects.order_by('-updated_at'), many=True).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات نوع الإستشارة'
            result.data = serialized_new_consult_type.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ نوع الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def read_consult_types_service():
    result = ResultView()
    try:
        all_consult_types = CoreModels.ConsultationType.objects.order_by('-updated_at')
        serialized_all_consult_types = CoreSerializers.ConsultationTypeSerializer(all_consult_types, many=True)
        result.data = serialized_all_consult_types.data
        result.msg = 'تم جلب أنواع الإستشارات بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب أنواع الإستشارات'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_consult_type_service(request_data, admin_id, consult_type_id):
    result = ResultView()
    try:
        request_data['updated_by_id'] = admin_id
        old_consult_type = CoreModels.ConsultationType.objects.get(id=consult_type_id)
        serialized_update_consult_type = CoreSerializers.ConsultationTypeSerializer(old_consult_type, data=request_data, partial=True)
        if serialized_update_consult_type.is_valid():
            serialized_update_consult_type.save()
            result.msg = 'تم تحديث نوع الإستشارة بنجاح'
            result.data = CoreSerializers.ConsultationTypeSerializer(CoreModels.ConsultationType.objects.order_by('-updated_at'), many=True).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات نوع الإستشارة'
            result.data = serialized_update_consult_type.errors
    except CoreModels.ConsultationType.DoesNotExist as e:
        result.msg = 'نوع الإستشارة غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث نوع الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_consult_type_service(consult_type_id):
    result = ResultView()
    try:
        delete_count, _ = CoreModels.ConsultationType.objects.filter(id=consult_type_id).delete()
        if delete_count == 0:
            raise CoreModels.ConsultationType.DoesNotExist()
        result.msg = 'تم حذف نوع الإستشارة بنجاح'
        result.is_success = True
    except CoreModels.ConsultationType.DoesNotExist as e:
        result.msg = 'نوع الإستشارة غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف نوع الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_hidden_consult_type_service(consult_type_id, admin_obj):
    result = ResultView()
    try:
        consult_type = CoreModels.ConsultationType.objects.get(id=consult_type_id)
        consult_type.is_deleted = not consult_type.is_deleted
        consult_type.updated_by = admin_obj
        consult_type.save()
        result.msg = f'تم {'إخفاء' if consult_type.is_deleted else 'إظهار'} نوع الإستشارة بنجاح'
        result.data = CoreSerializers.ConsultationTypeSerializer(consult_type).data
        result.is_success = True
    except CoreModels.ConsultationType.DoesNotExist as e:
        result.msg = 'نوع الإستشارة غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إخفاء / إظهار نوع الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Consultation
def create_consultation_service(request_data, admin_id):
    result = ResultView()
    try:
        request_data['created_by_id'] = admin_id
        serialized_new_consultation = CoreSerializers.ConsultationSerializer(data=request_data)
        if serialized_new_consultation.is_valid():
            serialized_new_consultation.save()
            result.msg = 'تم إضافة الإستشارة بنجاح'
            result.data = CoreSerializers.ConsultationSerializer(
                CoreModels.Consultation.objects.filter(consultation_type=request_data.get('consultation_type_id') ).order_by('-updated_at'),
                many=True
            ).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات الإستشارة'
            result.data = serialized_new_consultation.errors
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حفظ الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def read_consultations_service(consultation_type_id):
    result = ResultView()
    try:
        all_consultations = CoreModels.Consultation.objects.filter(consultation_type=consultation_type_id).order_by('-updated_at')
        serialized_all_consultations = CoreSerializers.ConsultationSerializer(all_consultations, many=True)
        result.data = serialized_all_consultations.data
        result.msg = 'تم جلب الإستشارات بنجاح'
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب الإستشارات'
        result.data = {'errors': str(e)}
    finally:
        return result

def update_consultation_service(request_data, admin_id, consultation_id):
    result = ResultView()
    try:
        request_data['updated_by_id'] = admin_id
        old_consultation = CoreModels.Consultation.objects.get(id=consultation_id)
        serialized_update_consultation = CoreSerializers.ConsultationSerializer(old_consultation, data=request_data, partial=True)
        if serialized_update_consultation.is_valid():
            serialized_update_consultation.save()
            result.msg = 'تم تحديث الإستشارة بنجاح'
            result.data = CoreSerializers.ConsultationSerializer(
                CoreModels.Consultation.objects.filter(consultation_type=old_consultation.consultation_type).order_by('-updated_at'),
                many=True,
            ).data
            result.is_success = True
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات الإستشارة'
            result.data = serialized_update_consultation.errors
    except CoreModels.Consultation.DoesNotExist as e:
        result.msg = 'الإستشارة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء تحديث الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_consultation_service(consultation_id):
    result = ResultView()
    try:
        delete_count, _ = CoreModels.Consultation.objects.filter(id=consultation_id).delete()
        if delete_count == 0:
            raise CoreModels.Consultation.DoesNotExist()
        result.msg = 'تم حذف الإستشارة بنجاح'
        result.is_success = True
    except CoreModels.Consultation.DoesNotExist as e:
        result.msg = 'الإستشارة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_hidden_consultation_service(consultation_id, admin_obj):
    result = ResultView()
    try:
        consultation = CoreModels.Consultation.objects.get(id=consultation_id)
        consultation.is_deleted = not consultation.is_deleted
        consultation.updated_by = admin_obj
        consultation.save()
        result.msg = f'تم {'إخفاء' if consultation.is_deleted else 'إظهار'} الإستشارة بنجاح'
        result.data = CoreSerializers.ConsultationSerializer(consultation).data
        result.is_success = True
    except CoreModels.Consultation.DoesNotExist as e:
        result.msg = 'الإستشارة غير موجودة'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إخفاء / إظهار الإستشارة'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region Client Reviews
def read_reviews_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        all_reviews = CoreModels.ClientReview.objects.all().order_by('-created_at')
        all_reviews_count = all_reviews.count()
        if all_reviews_count <= 0:
            raise ValueError('لا يوجد تقييمات متاحة للعرض')
        paginator = Paginator(all_reviews, page_size)
        page = paginator.get_page(page_number)
        serialized_all_reviews = AdminSerializers.ClientReviewSerializer(page.object_list, many=True)
        result.msg = 'تم جلب تقييمات العملاء بنجاح'
        result.is_success = True
        result.data = {
            "all": serialized_all_reviews.data,
            "pagination": {
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "current_page": page.number,
                "has_next": page.has_next(),
                "has_previous": page.has_previous()
            }
        }
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء جلب تقييمات العملاء'
        result.data = {'errors': str(e)}
    finally:
        return result

def toggle_hidden_review_service(review_id, admin_id):
    result = ResultView()
    try:
        review_obj = CoreModels.ClientReview.objects.get(id=review_id)
        review_obj.is_deleted = not review_obj.is_deleted
        review_obj.updated_by_id = admin_id
        review_obj.save()
        result.msg = f'تم {'إخفاء' if review_obj.is_deleted else 'إظهار'} تقييم العميل بنجاح'
        result.is_success = True
    except CoreModels.ClientReview.DoesNotExist as e:
        result.msg = 'تقييم العميل غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء إخفاء / إظهار تقييم العميل'
        result.data = {'errors': str(e)}
    finally:
        return result

def delete_review_service(review_id):
    result = ResultView()
    try:
        review_obj = CoreModels.ClientReview.objects.get(id=review_id)
        review_obj.delete()
        result.msg = 'تم حذف تقييم العميل بنجاح'
        result.is_success = True
    except CoreModels.ClientReview.DoesNotExist as e:
        result.msg = 'تقييم العميل غير موجود'
        result.data = {'errors': str(e)}
    except Exception as e:
        result.msg = 'حدث خطأ غير متوقع أثناء حذف تقييم العميل'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

