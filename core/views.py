from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core import services

# Create your views here.

# region Units
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def propose_unit_view(request):
    propose_result = services.propose_unit_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if propose_result.is_success
        else status.HTTP_401_UNAUTHORIZED if propose_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(propose_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_unit_view(request):
    request_result = services.request_unit_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_201_CREATED if request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if request_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(request_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paginated_client_requests_view(request):
    requests_result = services.paginated_client_requests_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_200_OK if requests_result.is_success
        else status.HTTP_401_UNAUTHORIZED if requests_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(requests_result.to_dict(), status=status_code)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cancel_request_view(request, request_id):
    cancel_request_result = services.cancel_request_service(request_id)
    status_code = (
        status.HTTP_200_OK if cancel_request_result.is_success
        else status.HTTP_401_UNAUTHORIZED if cancel_request_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(cancel_request_result.to_dict(), status=status_code)

@api_view(["GET"])
def proposal_form_data_view(request):
    form_data_result = services.proposal_form_data_service()
    status_code = (
        status.HTTP_200_OK if form_data_result.is_success
        else status.HTTP_401_UNAUTHORIZED if form_data_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(form_data_result.to_dict(), status=status_code)

@api_view(["GET"])
def recent_units_view(request):
    recent_units_result = services.recent_units_service()
    status_code = (
        status.HTTP_200_OK if recent_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if recent_units_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(recent_units_result.to_dict(), status=status_code)

@api_view(["POST"])
def filter_paginated_units_view(request):
    filter_paginated_units_result = services.filter_paginated_units_service(request.data, request.user.id)
    status_code = (
        status.HTTP_201_CREATED if filter_paginated_units_result.is_success
        else status.HTTP_401_UNAUTHORIZED if filter_paginated_units_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(filter_paginated_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def unit_details_view(request, unit_id):
    unit_details_result = services.unit_details_service(unit_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if unit_details_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(unit_details_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paginated_client_units_view(request):
    paginated_client_units_result = services.paginated_client_units_service(request.data, request.user.id if request.user else None)
    status_code = (
        status.HTTP_200_OK if paginated_client_units_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(paginated_client_units_result.to_dict(), status=status_code)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_update_unit_view(request, unit_id):
    result = services.get_update_unit_service(unit_id, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_404_NOT_FOUND if result.msg.lower().__contains__('غير موجودة')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_unit_view(request):
    result = services.update_unit_service(request.data, request.user)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_404_NOT_FOUND if result.msg.lower().__contains__('غير موجودة')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_unit_view(request, unit_id):
    result = services.soft_delete_unit_service(unit_id, request.user.id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def hard_delete_unit_view(request, unit_id):
    result = services.hard_delete_unit_service(unit_id)
    status_code = (
        status.HTTP_200_OK if result.is_success
        else status.HTTP_401_UNAUTHORIZED if result.msg.lower().__contains__('غير مصرح')
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(result.to_dict(), status=status_code)
# endregion

# region Home
@api_view(["GET"])
def home_top_reviews_view(request):
    reviews_result = services.home_reviews_service()
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
def home_consultation_types_view(request):
    consultation_types_result = services.home_consultation_types_service()
    status_code = (
        status.HTTP_200_OK if consultation_types_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(consultation_types_result.to_dict(), status=status_code)

@api_view(["GET"])
def consultations_by_type_view(request, consult_type_id):
    consultations_result = services.consultations_by_type_service(consult_type_id)
    status_code = (
        status.HTTP_200_OK if consultations_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(consultations_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_featured_units_view(request):
    featured_units_result = services.home_featured_units_service()
    status_code = (
        status.HTTP_200_OK if featured_units_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(featured_units_result.to_dict(), status=status_code)

@api_view(["GET"])
def home_most_viewed_units_view(request):
    most_viewed_units_result = services.home_most_viewed_units_service()
    status_code = (
        status.HTTP_200_OK if most_viewed_units_result.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(most_viewed_units_result.to_dict(), status=status_code)
# endregion

# region Reviews
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_review_view(request):
    send_result = services.add_review_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if send_result.is_success
        else status.HTTP_401_UNAUTHORIZED if send_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)
# endregion

# region Draw Results
@api_view(["POST"])
def draw_results_view(request):
    draw_results = services.draw_results_service(request.data)
    status_code = (
        status.HTTP_200_OK if draw_results.is_success
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return Response(draw_results.to_dict(), status=status_code)
# endregion

# region Contact Us
@api_view(["POST"])
def add_contact_us_msg_view(request):
    send_result = services.add_contact_us_msg_service(request.data)
    status_code = (
        status.HTTP_201_CREATED if send_result.is_success
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(send_result.to_dict(), status=status_code)
# endregion

# region Favorites
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_favorite_view(request):
    add_favorite_result = services.add_favorite_service(request.data, request.headers)
    status_code = (
        status.HTTP_201_CREATED if add_favorite_result.is_success
        else status.HTTP_401_UNAUTHORIZED if add_favorite_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(add_favorite_result.to_dict(), status=status_code)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def list_paginated_favorites_view(request):
    list_favorites_result = services.list_favorites_service(request.data, request.headers)
    status_code = (
        status.HTTP_200_OK if list_favorites_result.is_success
        else status.HTTP_401_UNAUTHORIZED if list_favorites_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(list_favorites_result.to_dict(), status=status_code)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_favorite_view(request, favorite_id):
    delete_favorite_result = services.delete_favorite_service(favorite_id)
    status_code = (
        status.HTTP_200_OK if delete_favorite_result.is_success
        else status.HTTP_401_UNAUTHORIZED if delete_favorite_result.msg.lower().__contains__('unauthorized')
        else status.HTTP_400_BAD_REQUEST
    )
    return Response(delete_favorite_result.to_dict(), status=status_code)
# endregion



