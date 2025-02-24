from core import models as CoreModels
from users import models as UsersModels
from core import serializers as CoreSerializers
from admindash import serializers as AdminSerializers
from core.base_models import ResultView
from users.utils import extract_payload_from_jwt
from django.db.models import Value, CharField, Q
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import StringAgg
import logging

# Create your services here.

def paginated_staff_service(request_data, request_headers):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '').replace('Bearer ', '')
        user_id = extract_payload_from_jwt(token).get('user_id')
        user_obj = UsersModels.CustomUser.objects.get(id=user_id)
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
        serialized_units = AdminSerializers.GetAllStaffSerializer(all_staff_q, many=True)
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



