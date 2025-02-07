from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from core.services import create_base_property_request_service, propose_land_service

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
def propose_land_view(request):
    propose_result = propose_land_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if propose_result.is_success
        else status.HTTP_401_UNAUTHORIZED if propose_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(propose_result.to_dict(), status=status_code)
'''
input
{
    "arabic": true,  // this indicates the language of the result should be in english or arabic (Arabic if true else or not provided english)
    "phone_number": "3232323",
    "project_id": "1",
    "project_type_id": "1",
    "city_id": "1",
    "area": 400,
    "payment_method": "CS",
    "first_installment_value": "25000",
    "installment_period": "5"
}
output
{
    "is_success": true,
    "data": {
        "phone_number": "3232323",
        "project": "The most distinguished",
        "project_type": "Lands",
        "city": "6th Of October",
        "first_installment_value": "25000",
        "installment_period": "5"
    },
    "msg": "Request saved successfully"
}

{
    "detail": "User not found",
    "code": "user_not_found"
}
'''
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_land_request_view(request):
    request_result = create_base_property_request_service(request.data, request.headers, land=True, buy=True)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_unit_request_view(request):
    request_result = create_base_property_request_service(request.data, request.headers, land=False, buy=True)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)
