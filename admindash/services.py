from core import models as CoreModels
from users import models as UsersModels
from django.contrib.auth.models import Group
from core import serializers as CoreSerializers
from admindash import serializers as AdminSerializers
from core.base_models import ResultView
from django.db.models import Value, CharField, Q
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import StringAgg
import logging

# Create your services here.

# region staff
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
        all_staff_count = all_staff_q.count()
        if all_staff_count <= 0:
            raise ValueError('لا يوجد موظفين للعرض')
        if all_staff_count > page_size*(page_number-1):
            all_staff_q = all_staff_q[page_size*(page_number-1):page_size*page_number]
        else:
            all_staff_q = all_staff_q[page_size*int(all_staff_count/page_size) if all_staff_count%page_size!=0 else int(all_staff_count/page_size)-1:]
            page_number = int(all_staff_count/page_size) if all_staff_count%page_size == 0 else int(all_staff_count/page_size)+1
        serialized_units = AdminSerializers.GetAllUserSerializer(all_staff_q, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_staff_count,
                "total_pages": all_staff_count/int(all_staff_count/page_size) if all_staff_count%page_size == 0 else int(all_staff_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_staff_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
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
        # role_id = request_data.pop('role_id')
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
            result.is_success = True
            result.msg = 'تم إضافة الموظف بنجاح'
            result.data = {
                "id": new_staff.instance.id,
                "first_name": new_staff.instance.first_name,
                "last_name": new_staff.instance.last_name,
                "username": new_staff.instance.username,
                "email": new_staff.instance.email,
                "date_joined": new_staff.instance.date_joined,
                "role": client_group.name,
                "referral_code": new_staff.instance.referral_code,
                "referral_count": new_staff.instance.referral_count
            }
        else:
            result.msg = 'حدث خطأ أثناء معالجة بيانات الموظف'
            result.data = new_staff.errors
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
# endregion

# region client
def paginated_clients_service(request_data):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 10)
        all_clients_q = UsersModels.CustomUser.objects.filter(groups__name='Clients')
        all_clients_count = all_clients_q.count()
        if all_clients_count <= 0:
            raise ValueError('لا يوجد عملاء للعرض')
        if all_clients_count > page_size*(page_number-1):
            all_clients_q = all_clients_q[page_size*(page_number-1):page_size*page_number]
        else:
            all_clients_q = all_clients_q[page_size*int(all_clients_count/page_size) if all_clients_count%page_size!=0 else int(all_clients_count/page_size)-1:]
            page_number = int(all_clients_count/page_size) if all_clients_count%page_size == 0 else int(all_clients_count/page_size)+1
        serialized_units = AdminSerializers.GetAllUserSerializer(all_clients_q, many=True)
        result.data = {
            "all": serialized_units.data,
            "pagination": {
                "total_items": all_clients_count,
                "total_pages": all_clients_count/int(all_clients_count/page_size) if all_clients_count%page_size == 0 else int(all_clients_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_clients_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات العملاء بنجاح'
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات العملاء'
        result.data = {'errors': str(e)}
    finally:
        return result
# endregion

# region unit
def unit_requests_user_service(unit_id):
    result = ResultView()
    try:
        # page_number = request_data.get('page_number', 1)
        # page_size = request_data.get('page_size', 10)
        all_unit_requests_query = CoreModels.UnitRequest.objects.filter(unit__id=unit_id).order_by('created_at')
        all_unit_requests_count = all_unit_requests_query.count()
        if all_unit_requests_count <= 0:
            raise ValueError('لا يوجد طلبات لهذه الوحدة')
        # if all_unit_requests_count > page_size*(page_number-1):
        #     all_requests_q = all_requests_q[page_size*(page_number-1):page_size*page_number]
        # else:
        #     all_requests_q = all_requests_q[page_size*int(all_unit_requests_count/page_size) if all_unit_requests_count%page_size!=0 else int(all_unit_requests_count/page_size)-1:]
            # page_number = int(all_unit_requests_count/page_size) if all_unit_requests_count%page_size == 0 else int(all_unit_requests_count/page_size)+1
        serialized_user_requests = AdminSerializers.UnitRequestSerializer(all_unit_requests_query, many=True)
        any_unit = all_unit_requests_query.first().unit
        price = any_unit.over_price if any_unit.over_price else any_unit.total_price if any_unit.total_price else any_unit.meter_price
        price_type = 'سعر الأوفر' if any_unit.over_price else 'السعر الإجمالى' if any_unit.total_price else 'سعر المتر'
        result.data = {
            "users": serialized_user_requests.data,
            "unit_data": {
                'id': unit_id,
                'title': any_unit.title,
                'area': any_unit.area,
                'price_obj': {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': any_unit.get_currency_display()}
            }
            # "pagination": {
            #     "total_items": all_unit_requests_count,
            #     "total_pages": all_unit_requests_count/int(all_unit_requests_count/page_size) if all_unit_requests_count%page_size == 0 else int(all_unit_requests_count/page_size)+1,
            #     "current_page": page_number,
            #     "has_next": True if all_unit_requests_count > page_size*page_number else False,
            #     "has_previous": True if page_number > 1 else False
            # }
        }
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
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 10)
        all_units_q = CoreModels.Unit.objects.order_by('created_at')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد طلبات وحدات متاحة للعرض')
        if all_units_count > page_size*(page_number-1):
            all_units_q = all_units_q[page_size*(page_number-1):page_size*page_number]
        else:
            all_units_q = all_units_q[page_size*int(all_units_count/page_size) if all_units_count%page_size!=0 else int(all_units_count/page_size)-1:]
            page_number = int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1
        serialized_units = AdminSerializers.AllUnitSerializer(all_units_q, many=True)
        result.data = {
            "all": serialized_units.data,
            "statuses": CoreModels.Status.objects.values('id', 'name', 'code', 'color'),
            "pagination": {
                "total_items": all_units_count,
                "total_pages": all_units_count/int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_units_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الطلبات بنجاح'
    except ValueError as ve:
        result.msg = str(ve)
        result.is_success = True
    except Exception as e:
        logging.error(f'Unexpected error occurred: {str(e)}')
        result.msg = 'حدث خطأ غير متوقع أثناء جلب بيانات الطلبات'
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
# endregion

# region contact us
def paginated_contact_msgs_service(request_data):
    result = ResultView()
    try:
        page_number = request_data.get('page_number', 1)
        page_size = request_data.get('page_size', 10)
        all_msgs_q = CoreModels.ContactUs.objects.all()
        all_msgs_count = all_msgs_q.count()
        if all_msgs_count <= 0:
            raise ValueError('لا يوجد رسائل للعرض')
        if all_msgs_count > page_size*(page_number-1):
            all_msgs_q = all_msgs_q[page_size*(page_number-1):page_size*page_number]
        else:
            all_msgs_q = all_msgs_q[page_size*int(all_msgs_count/page_size) if all_msgs_count%page_size!=0 else int(all_msgs_count/page_size)-1:]
            page_number = int(all_msgs_count/page_size) if all_msgs_count%page_size == 0 else int(all_msgs_count/page_size)+1
        serialized_msgs = CoreSerializers.ContactUsSerializer(all_msgs_q, many=True)
        result.data = {
            "all": serialized_msgs.data,
            "pagination": {
                "total_items": all_msgs_count,
                "total_pages": all_msgs_count/int(all_msgs_count/page_size) if all_msgs_count%page_size == 0 else int(all_msgs_count/page_size)+1,
                "current_page": page_number,
                "has_next": True if all_msgs_count > page_size*page_number else False,
                "has_previous": True if page_number > 1 else False
            }
        }
        result.is_success = True
        result.msg = 'تم جلب بيانات الرسائل بنجاح'
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

# endregion











