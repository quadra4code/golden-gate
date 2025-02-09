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
def proposal_form_data_view(request):
    form_data_result = services.proposal_form_data_service()
    status_code = (
        status.HTTP_201_CREATED if form_data_result.is_success
        else status.HTTP_401_UNAUTHORIZED if form_data_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(form_data_result.to_dict(), status=status_code)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def all_properties_view(request):
    all_units_result = services.all_properties_service()
    status_code = (
        status.HTTP_201_CREATED if all_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if all_units_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(all_units_result.to_dict(), status=status_code)

@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def filter_properties_view(request):
    filter_units_result = services.filter_properties_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if filter_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if filter_units_result.msg.__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(filter_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_top_reviews_view(request):
    reviews_result = services.client_property_reviews_service()
    status_code = (
        status.HTTP_200_OK if reviews_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(reviews_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_articles_view(request):
    articles_result = services.home_articles_service()
    status_code = (
        status.HTTP_200_OK if articles_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(articles_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_consultations_view(request):
    consultations_result = services.home_consultations_service()
    status_code = (
        status.HTTP_200_OK if consultations_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(consultations_result.to_dict(), status=status_code)


@api_view(["GET"])
def draw_results_view(request):
    draw_results = services.draw_results_service()
    status_code = (
        status.HTTP_200_OK if draw_results.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(draw_results.to_dict(), status=status_code)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_draw_result_view(request):
    send_result = services.add_draw_result_service(request.data, request.headers)
    status_code = (
        status.HTTP_200_OK if send_result.is_success
        else status.HTTP_401_UNAUTHORIZED if send_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)
