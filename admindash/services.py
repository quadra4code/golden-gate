from core import models as CoreModels
from users import models as UsersModels
from django.contrib.auth.models import Group
from core import serializers as CoreSerializers
from admindash import serializers as AdminSerializers
from core.base_models import ResultView
from django.db.models import Value, CharField, Q, Count
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.auth import authenticate
from users.utils import generate_jwt_token
import logging

# Create your services here.

# region staff
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
# endregion

# region client
def paginated_clients_service(request_data):
    result = ResultView()
    try:
        page_number = int(request_data.get('page_number', 1))
        page_size = int(request_data.get('page_size', 10))
        all_clients_q = UsersModels.CustomUser.objects.filter(groups__name='Client')
        all_clients_count = all_clients_q.count()
        if all_clients_count <= 0:
            raise ValueError('لا يوجد عملاء للعرض')
        # if all_clients_count > page_size*(page_number-1):
        #     all_clients_q = all_clients_q[page_size*(page_number-1):page_size*page_number]
        # else:
        #     all_clients_q = all_clients_q[page_size*int(all_clients_count/page_size) if all_clients_count%page_size!=0 else int(all_clients_count/page_size)-1:]
        #     page_number = int(all_clients_count/page_size) if all_clients_count%page_size == 0 else int(all_clients_count/page_size)+1
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
        # total_pages = (all_unit_requests_count + page_size - 1) // page_size
        # page_number = min(page_number, total_pages)
        # start_index = (page_number - 1) * page_size
        # end_index = start_index + page_size
        # all_unit_requests_query = all_unit_requests_query[start_index:end_index]
        serialized_user_requests = AdminSerializers.UnitRequestSerializer(all_unit_requests_query, many=True)
        any_unit = all_unit_requests_query.first().unit
        price = any_unit.over_price if any_unit.over_price else any_unit.total_price if any_unit.total_price else any_unit.meter_price
        price_type = 'الأوفر' if any_unit.over_price else 'الإجمالى' if any_unit.total_price else 'سعر المتر'
        currency = any_unit.get_over_price_currency_display() if any_unit.over_price else any_unit.get_total_price_currency_display() if any_unit.total_price else any_unit.get_meter_price_currency_display()
        result.data = serialized_user_requests.data
        # result.data = {
        #     "users": serialized_user_requests.data,
        #     "unit_data": {
        #         'id': unit_id,
        #         'title': any_unit.title,
        #         'area': any_unit.area,
        #         'price_obj': {'price_type': price_type, 'price_value': f'{price:,.0f}', 'currency': currency}
        #     }
            # "pagination": {
            #     "total_items": all_unit_requests_count,
            #     "total_pages": total_pages,
            #     "current_page": page_number,
            #     "has_next": page_number < total_pages,
            #     "has_previous": page_number > 1
            # }
        # }
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
        all_units_q = CoreModels.Unit.objects.annotate(
            requests_count=Count('unitrequest')  # Assuming 'unitrequest' is the related name
        ).order_by('-requests_count')
        all_units_count = all_units_q.count()
        if all_units_count <= 0:
            raise ValueError('لا يوجد طلبات وحدات متاحة للعرض')
        # if all_units_count > page_size*(page_number-1):
        #     all_units_q = all_units_q[page_size*(page_number-1):page_size*page_number]
        # else:
        #     all_units_q = all_units_q[page_size*int(all_units_count/page_size) if all_units_count%page_size!=0 else int(all_units_count/page_size)-1:]
        #     page_number = int(all_units_count/page_size) if all_units_count%page_size == 0 else int(all_units_count/page_size)+1
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
        # if all_msgs_count > page_size*(page_number-1):
        #     all_msgs_q = all_msgs_q[page_size*(page_number-1):page_size*page_number]
        # else:
        #     all_msgs_q = all_msgs_q[page_size*int(all_msgs_count/page_size) if all_msgs_count%page_size!=0 else int(all_msgs_count/page_size)-1:]
        #     page_number = int(all_msgs_count/page_size) if all_msgs_count%page_size == 0 else int(all_msgs_count/page_size)+1
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
            result.data = serialized_new_article.data
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
        all_articles = CoreModels.Article.objects.order_by('-created_at')
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
            result.data = serialized_update_article.data
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

# region Consultation

# endregion









