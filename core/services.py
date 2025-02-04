from core import models
from core import serializers
from core.base_models import ResultView
from users.utils import extract_payload_from_jwt
# Create your services here.

def create_base_property_request_service(request_data, request_headers, land=True, buy=True):
    result = ResultView()
    try:
        token = request_headers.get('Authorization', '')
        token_decode_result = extract_payload_from_jwt(token=str.replace(token, 'Bearer ', ''))
        arabic = request_data.get('arabic', False)
        serialized_land_request = serializers.LandSerializer(data=request_data)
        if serialized_land_request.is_valid():
            
        # phone_number = request_data.get('phone_number', '')
        # project_id = request_data.get('project_id', '')
        # project_type_id = request_data.get('project_type_id', '')
        # city_id = request_data.get('city_id', '')
        # payment_method = request_data.get('payment_method', '')
        # first_installment_value = request_data.get('first_installment_value', '')
        # installment_period = request_data.get('installment_period', '')
        # area = request_data.get('area', '')
            pcp_obj = models.PCP.objects.get_or_create(project=project_id, project_type=project_type_id, city=city_id)[0]
            status_obj = models.Status.objects.filter(code=0).first()
            kwargs = {
                'pcp': pcp_obj,
                'payment_method': serialized_land_request.data.get('payment_method'),
                'first_installment_value': serialized_land_request.data.get('first_installment_value'),
                'installment_period': serialized_land_request.data.get('installment_period'),
                'area': serialized_land_request.data.get('area'),
                'status': status_obj,
                'phone_number': serialized_land_request.data.get('phone_number'),
                'created_by_id': token_decode_result.get('user_id')
            }
            for key, val in kwargs.items():
                print(key, val)
            # models.Land.objects.create(**kwargs)
            # result.data = {
            #     'phone_number': phone_number,
            #     'project': pcp_obj.project.name_ar if arabic else pcp_obj.project.name_en,
            #     'project_type': pcp_obj.project_type.name_ar if arabic else pcp_obj.project_type.name_en,
            #     'city': pcp_obj.city.name_ar if arabic else pcp_obj.city.name_en,
            #     'area': area,
            #     'first_installment_value': first_installment_value,
            #     'installment_period': installment_period
            # }
            result.msg = 'Request saved successfully'
            result.is_success=True
    except Exception as e:
        result.msg = 'Unexpected error happened while saving request'
        result.data = {'error': str(e)}
    finally:
        return result


