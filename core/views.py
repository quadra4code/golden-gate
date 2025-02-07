from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from core import services

# Create your views here.

'''
input 
{
    "project_type_id": "1",
    "project_id": "2",
    "city_id": "7",
    "description": "thsislfj aljiaj;lf iaj fj;alej jwe jl",
    "area": "400",
    "payment_method": "IN",
    "installment_period": "5",
    "first_installment_value": "25000",
    "phone_number": "01118069749"
}
output
{
    "is_success":true,
    "data":{
        "pcp_id":26,
        "description":"thsislfj aljiaj;lf iaj fj;alej jwe jl",
        "area":400,
        "payment_method":"IN",
        "installment_period":5,
        "first_installment_value":"25000.0000",
        "phone_number":"01118069749",
        "created_by_id":1
    },
    "msg":"Request saved successfully"
}
'''
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def propose_property_view(request):
    propose_result = services.propose_property_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if propose_result.is_success
        else status.HTTP_401_UNAUTHORIZED if propose_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(propose_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_property_view(request):
    request_result = services.request_property_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def proposal_form_data_view(request):
    form_data_result = services.proposal_form_data_service()
    status_code = (
        status.HTTP_201_CREATED if form_data_result.is_success
        else status.HTTP_401_UNAUTHORIZED if form_data_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(form_data_result.to_dict(), status=status_code)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_properties_view(request):
    all_units_result = services.all_properties_service()
    status_code = (
        status.HTTP_201_CREATED if all_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if all_units_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(all_units_result.to_dict(), status=status_code)

