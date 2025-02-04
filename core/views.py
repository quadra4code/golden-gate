from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from core.services import create_base_property_request_service
# Create your views here.


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
